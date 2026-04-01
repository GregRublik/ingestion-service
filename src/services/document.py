import os
from typing import Optional, List

from exceptions import DocumentNoFoundException, ModelNoFoundException
from repositories.aws import AWSRepository

from repositories.document import DocumentRepository
from fastapi import UploadFile
from models.document import DocumentStatus
from schemas.document import DocumentResponse, DocumentUpdate
from services.unit_of_work import UnitOfWork
from config import settings

class DocumentService:
    """Service for working with documents"""

    def __init__(self, aws_repository: AWSRepository, document_repository: DocumentRepository, uow: UnitOfWork):
        self.aws_repository = aws_repository
        self.document_repository = document_repository
        self.uow = uow

    async def add_documents(self, bucket: str, files: list[UploadFile]):
        async with self.uow:
            list_added_documents = []
            for file in files:
                # Upload file to AWS S3
                await self.aws_repository.push_document(bucket, file.filename, file.file.read())

                # Save document metadata in the database
                db_document = await self.document_repository.add_one(self.uow.session,{
                    "file_name": file.filename,
                    "file_type": file.content_type,
                    "file_extension": os.path.splitext(file.filename)[1].lower(),
                    "file_size": file.size,
                    "storage_path": f"s3://{bucket}/{file.filename}",
                    "status": DocumentStatus.UPLOADED,
                })
                list_added_documents.append(db_document)

            return list_added_documents

    async def get_document(self, bucket: str, file_name: str):
        async with self.uow:
            return await self.aws_repository.get_document(bucket, file_name)

    async def get_document_by_id(self, doc_id: int) -> DocumentResponse:
        async with self.uow:
            return await self.document_repository.get_by_id(self.uow.session, doc_id)

    async def get_documents(self, status_filter: Optional[str] = None) -> List[DocumentResponse]:
        async with self.uow:
            if status_filter:
                documents = await self.document_repository.get_by_status(self.uow.session, status_filter)
            else:
                documents = await self.document_repository.get_all(self.uow.session)

            return documents

    async def update_document(self, doc_id: int, document: DocumentUpdate):
        async with self.uow:
            document = await self.document_repository.change_one(
                self.uow.session,
                doc_id,
                document.model_dump(exclude_unset=True)
            )
            return document

    async def delete_document(self, doc_id: int):
        async with self.uow:
            try:
                document = await self.document_repository.get_by_id(self.uow.session, doc_id)
                await self.aws_repository.delete_document(settings.aws.bucket_name, document.file_name)
                await self.document_repository.delete_by_id(self.uow.session, doc_id)
            except ModelNoFoundException:
                raise DocumentNoFoundException