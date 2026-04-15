from fastapi import APIRouter, Depends, status
from services.normalization import NormalizationService

from depends import get_normalization_service
from exceptions import DocumentNoFoundException, DocumentException, APIException

router = APIRouter()

@router.post("/documents/{doc_id}/normalize")
async def run_normalize(
        doc_id: int,
        normalization_service: NormalizationService = Depends(get_normalization_service),
):
    try:
        await normalization_service.normalize_document(doc_id)
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
