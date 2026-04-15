
from fastapi import APIRouter, Depends, status

from services.chunk import ChunkService
from services.document import DocumentService

from schemas.chunk import ChunkRequest  # или куда положишь схему
from schemas.document import DocumentResponse

from depends import get_document_service, get_chunk_service

from exceptions import DocumentNoFoundException, APIException, DocumentException

router = APIRouter()

@router.post("/documents/{doc_id}/chunk", response_model=DocumentResponse)
async def chunk_document(
    doc_id: int,
    payload: ChunkRequest,
    chunk_service: ChunkService = Depends(get_chunk_service)
):
    try:
        return await chunk_service.chunk_document(
            doc_id,
            payload.chunk_type,
            payload.params
        )
    except DocumentNoFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
    except DocumentException as e:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=e.detail
        )