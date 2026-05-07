from fastapi import APIRouter, Depends, status
from services.embedding import EmbeddingService
from depends import get_embedding_service
from exceptions import APIException, DocumentNotFoundException

from schemas.embedding import ParamsVectorization
from config import settings

router = APIRouter()

@router.post("/documents/{doc_id}/embedding")
async def embedding_document(
    doc_id: int,
    params_vectorization: ParamsVectorization,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    try:
        return await embedding_service.embedding_document(doc_id, params_vectorization)

    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
