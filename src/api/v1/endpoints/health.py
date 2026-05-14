from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "orchestrator-service",
        "timestamp": datetime.now()
    }


@router.get("/ready")
async def readiness():
    # тут можно проверять зависимости:
    # БД, Redis, Kafka, другие сервисы
    return {
        "status": "ready"
    }


@router.get("/live")
async def liveness():
    return {
        "status": "alive"
    }