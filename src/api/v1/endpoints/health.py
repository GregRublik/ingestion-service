from fastapi import APIRouter
from datetime import datetime

from schemas.health import ResponseHealth, ResponseReady, ResponseLive, Status
from schemas.response import APIResponse, ok


router = APIRouter()


@router.get("/health", response_model=APIResponse[ResponseHealth])
async def health():
    return ok(
        ResponseHealth(
            service="orchestrator-service",
            timestamp=datetime.now()
        )
    )


@router.get("/ready", response_model=APIResponse[ResponseReady])
async def readiness():
    # TODO тут нужно проверять зависимости:  БД, Redis, Kafka, другие сервисы
    return ok(
        ResponseReady(
            status=Status.ready,
            timestamp=datetime.now()
        )
    )


@router.get("/live", response_model=APIResponse[ResponseLive])
async def liveness():
    return ok(
        ResponseLive(
            status=Status.live,
            timestamp=datetime.now()
        )
    )
