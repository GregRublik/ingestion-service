import os
from typing import Optional, List

from exceptions import (
    DocumentNotFoundException,
    ModelNotFoundException,
    DocumentAlreadyExistsException,
    ModelAlreadyExistsException
)
from repositories.aws import AWSRepository

from repositories.document import DocumentRepository
from fastapi import UploadFile
from models.document import DocumentStatus
from schemas.document import DocumentResponse, DocumentUpdate, DocumentDownloadUrlResponse, DocumentFilters
from services.unit_of_work import UnitOfWork
from config import settings

class DocumentService:
    """Service for working with documents"""

    def __init__(self, aws_repository: AWSRepository, document_repository: DocumentRepository, uow: UnitOfWork):
        self.aws_repository = aws_repository
        self.document_repository = document_repository
        self.uow = uow

    @staticmethod
    def _build_filters(filters: DocumentFilters) -> dict:

        result = {}

        if filters.status:
            result["status"] = filters.status

        if filters.file_extension:
            result["file_extension"] = filters.file_extension

        if filters.created_at_from:
            result["created_at__gte"] = filters.created_at_from

        if filters.created_at_to:
            result["created_at__lte"] = filters.created_at_to

        if filters.updated_at_from:
            result["updated_at__gte"] = filters.updated_at_from

        if filters.updated_at_to:
            result["updated_at__lte"] = filters.updated_at_to

        return result

    async def add_documents(self, bucket: str, files: list[UploadFile]):
        try:
            async with self.uow:
                list_added_documents = []
                for file in files:

                    # Save document metadata in the database
                    db_document = await self.document_repository.add_one(self.uow.session,{
                        "file_name": file.filename,
                        "file_type": file.content_type,
                        "file_extension": os.path.splitext(file.filename)[1].lower(),
                        "file_size": file.size,
                        "storage_path": f"s3://{bucket}/{file.filename}",
                        "status": DocumentStatus.uploaded,
                    })
                    list_added_documents.append(db_document)

                    # Upload file to AWS S3
                    await self.aws_repository.push_document(bucket, file.filename, file.file.read())

                return list_added_documents
        except ModelAlreadyExistsException as e:
            raise DocumentAlreadyExistsException

    async def get_document_by_id(self, doc_id: int) -> DocumentResponse:
        async with self.uow:
            try:
                return await self.document_repository.get_by_id(self.uow.session, doc_id)
            except ModelNotFoundException:
                raise DocumentNotFoundException
    async def get_documents(self, filters: DocumentFilters) -> List[DocumentResponse]:
        orm_filters = self._build_filters(filters)
        async with self.uow:
            documents = await self.document_repository.get_all(self.uow.session, orm_filters)
            return documents

    async def update_document(self, doc_id: int, document: DocumentUpdate):
        async with self.uow:
            try:
                return await self.document_repository.change_one(
                    self.uow.session,
                    doc_id,
                    document.model_dump(exclude_unset=True)
                )
            except ModelNotFoundException:
                raise DocumentNotFoundException

    async def delete_document(self, doc_id: int):
        async with self.uow:
            try:
                document = await self.document_repository.get_by_id(self.uow.session, doc_id)
                await self.aws_repository.delete_document(settings.aws.bucket_name, document.file_name)
                await self.document_repository.delete_by_id(self.uow.session, doc_id)
            except ModelNotFoundException:
                raise DocumentNotFoundException

    async def get_download_url(self, doc_id: int) -> DocumentDownloadUrlResponse:
        async with self.uow:
            try:
                document_db = await self.document_repository.get_by_id(self.uow.session, doc_id)
                url = await self.aws_repository.get_download_url(settings.aws.bucket_name, document_db.file_name)
                return DocumentDownloadUrlResponse(url=url)
            except ModelNotFoundException:
                raise DocumentNotFoundException