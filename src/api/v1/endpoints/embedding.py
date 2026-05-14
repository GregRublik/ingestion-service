from fastapi import APIRouter, Depends, status

from services.embedding import EmbeddingService
from schemas.embedding import ParamsVectorization, ResponseVectorization
from schemas.response import APIResponse

from response import ok, UnifiedResponseRoute
from depends import get_embedding_service
from exceptions import APIException, DocumentNotFoundException


router = APIRouter(prefix="/documents", route_class=UnifiedResponseRoute)


@router.post("/{doc_id}/embedding", response_model=APIResponse[ResponseVectorization])
async def embedding_document(
    doc_id: int,
    params_vectorization: ParamsVectorization,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    try:
        data = await embedding_service.embedding_document(doc_id, params_vectorization)
        return ok(data)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
