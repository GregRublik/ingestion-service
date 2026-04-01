from fastapi import APIRouter, Depends
from services.normalization import NormalizationService

from depends import get_normalization_service

router = APIRouter()

@router.get("/documents/{doc_id}/normalize")
async def run_normalize(
        doc_id: int,
        normalization_service: NormalizationService = Depends(get_normalization_service),
):
    await normalization_service.normalize_document(doc_id)
