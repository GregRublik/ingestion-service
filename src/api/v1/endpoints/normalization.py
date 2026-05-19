from fastapi import APIRouter, Depends, status

from services.normalization import NormalizationService
from schemas.document import DocumentResponse
from schemas.normalize import ParamsNormalize
from schemas.response import APIResponse, ok

from depends import get_normalization_service
from exceptions import DocumentNotFoundException, DocumentException, APIException, DocumentAlreadyExistsException


router = APIRouter(prefix="/documents")


@router.post("/{doc_id}/normalize", response_model=APIResponse[DocumentResponse])
async def normalize_document(
        doc_id: int,
        params_normalize: ParamsNormalize,
        normalization_service: NormalizationService = Depends(get_normalization_service),
):
    try:
        document = await normalization_service.normalize_document(doc_id, params_normalize)
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
