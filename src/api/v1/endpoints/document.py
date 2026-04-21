from fastapi import APIRouter, Depends, status, UploadFile
from typing import List, Optional
from services.document import DocumentService
from depends import get_document_service
from schemas.document import DocumentResponse, DocumentUpdate, DocumentDownloadUrlResponse
from exceptions import DocumentNotFoundException, APIException, DocumentException, DocumentAlreadyExistsException
from fastapi.responses import StreamingResponse
from config import settings
import urllib.parse

router = APIRouter()

@router.post("/documents", response_model=List[DocumentResponse])
async def create_documents(
    docs: List[UploadFile],
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        return await document_service.add_documents(settings.aws.bucket_name, docs)
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

@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        return await document_service.get_document_by_id(doc_id)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )

@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(
    status_filter: Optional[str] = None,
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        return await document_service.get_documents(status_filter=status_filter)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )

@router.patch("/documents/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: int,
    payload: DocumentUpdate,
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        return await document_service.update_document(doc_id, payload)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )

@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        await document_service.delete_document(doc_id)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )

@router.get("/documents/{doc_id}/download", response_model=DocumentDownloadUrlResponse)
async def get_download_url_document(
    doc_id: int,
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        return await document_service.get_download_url(doc_id)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )