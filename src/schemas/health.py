from datetime import datetime
from pydantic import BaseModel
from enum import StrEnum

class Status(StrEnum):
    ready = "ready"
    live = "live"

class ResponseHealth(BaseModel):
    service: str
    timestamp: datetime

class ResponseReady(BaseModel):
    status: Status = Status.ready
    timestamp: datetime

class ResponseLive(ResponseReady):
    status: Status = Status.live
