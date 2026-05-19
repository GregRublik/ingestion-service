from fastapi import APIRouter, Depends

from services.embedding import EmbeddingService
from schemas.embedding import ParamsVectorization, ResponseVectorization
from schemas.response import APIResponse, ok

from depends import get_embedding_service


router = APIRouter(prefix="/documents")


@router.post("/{doc_id}/embedding", response_model=APIResponse[ResponseVectorization])
async def embedding_document(
    doc_id: int,
    params_vectorization: ParamsVectorization,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    data = await embedding_service.embedding_document(doc_id, params_vectorization)
    return ok(data)
