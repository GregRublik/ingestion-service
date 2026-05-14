from fastapi import APIRouter, Depends, status

from services.chunk import ChunkService

from schemas.chunk import ChunkRequest
from schemas.document import DocumentResponse
from schemas.response import APIResponse

from depends import get_chunk_service
from exceptions import DocumentNotFoundException, APIException, DocumentException, DocumentAlreadyExistsException
from response import ok, UnifiedResponseRoute


router = APIRouter(prefix="/documents", route_class=UnifiedResponseRoute)


@router.post("/{doc_id}/chunk", response_model=APIResponse[DocumentResponse])
async def chunk_document(
    doc_id: int,
    payload: ChunkRequest,
    chunk_service: ChunkService = Depends(get_chunk_service)
):
    """method for starting document chunking"""

    try:
        document = await chunk_service.chunk_document(doc_id, payload.chunk_type, payload.params)
        return ok(document)
    except DocumentNotFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
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