from typing import List, Optional

from fastapi import APIRouter, Depends, status, UploadFile

from config import settings
from services.document import DocumentService
from depends import get_document_service
from schemas.document import DocumentResponse, DocumentUpdate, DocumentDownloadUrlResponse, DocumentFilters
from schemas.response import APIResponse, ok
from exceptions import DocumentNotFoundException, APIException, DocumentException, DocumentAlreadyExistsException



router = APIRouter(prefix="/documents")


@router.post("/", response_model=APIResponse[List[DocumentResponse]])
async def create_documents(
    docs: List[UploadFile],
    document_service: DocumentService = Depends(get_document_service),
):
    """Create document"""
    try:
        document = await document_service.add_documents(settings.aws.bucket_name, docs)
        return ok(document)
    except DocumentException as e:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=e.detail
        )
    except DocumentAlreadyExistsException as e:
        raise APIException(
            status_code=status.HTTP_409_CONFLICT,
            error=e.detail
        )


@router.get("/{doc_id}", response_model=APIResponse[DocumentResponse])
async def get_document(
    doc_id: int,
    document_service: DocumentService = Depends(get_document_service),
):
    """Get document"""
    try:
        document = await document_service.get_document_by_id(doc_id)
        return ok(document)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )


@router.get("/", response_model=APIResponse[List[DocumentResponse]])
async def get_documents(
    filters: DocumentFilters = Depends(),
    document_service: DocumentService = Depends(get_document_service),
):
    """Get documents"""
    try:
        documents = await document_service.get_documents(filters=filters)
        return ok(documents)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )


@router.patch("/{doc_id}", response_model=APIResponse[DocumentResponse])
async def update_document(
    doc_id: int,
    payload: DocumentUpdate,
    document_service: DocumentService = Depends(get_document_service),
):
    """Update document"""
    try:
        document = await document_service.update_document(doc_id, payload)
        return ok(document)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    document_service: DocumentService = Depends(get_document_service),
):
    """Delete document"""
    try:
        await document_service.delete_document(doc_id)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )


@router.get("/{doc_id}/download", response_model=APIResponse[DocumentDownloadUrlResponse])
async def get_download_url_document(
    doc_id: int,
    document_service: DocumentService = Depends(get_document_service),
):
    """Get download url document"""
    try:
        url_document = await document_service.get_download_url(doc_id)
        return ok(url_document)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
