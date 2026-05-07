from fastapi import APIRouter, Depends, status
from services.normalization import NormalizationService

from depends import get_normalization_service
from exceptions import DocumentNotFoundException, DocumentException, APIException, DocumentAlreadyExistsException
from schemas.document import DocumentResponse, ParamsNormalize

router = APIRouter()

@router.post("/documents/{doc_id}/normalize", response_model=DocumentResponse)
async def normalize_document(
        doc_id: int,
        params_normalize: ParamsNormalize,
        normalization_service: NormalizationService = Depends(get_normalization_service),
):
    try:
        return await normalization_service.normalize_document(doc_id, params_normalize)

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
