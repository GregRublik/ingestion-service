from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Literal
from enum import StrEnum

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    NORMALIZED = "normalized"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"

class DocumentResponse(BaseModel):
    id: int
    file_name: str
    file_extension: str
    file_type: str
    file_size: int
    storage_path: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
    meta: Optional[Dict] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True  # Для поддержки работы с SQLAlchemy моделями

class DocumentCreate(BaseModel):
    file_name: str
    file_type: str
    file_size: int
    storage_path: str
    meta: Optional[Dict] = None

class DocumentUpdate(BaseModel):
    status: DocumentStatus
    error_message: Optional[str] = None
    meta: Optional[Dict] = None

class DocumentMetadataResponse(BaseModel):
    file_name: str
    file_type: str
    file_size: int
    meta: Optional[Dict] = None
    error_message: Optional[str] = None

class DocumentDownloadUrlResponse(BaseModel):
    url: str


class StrategyMode(StrEnum):
    base = "base"
    questions_and_answers = "questions_and_answers"

class ParamsNormalize(BaseModel):
    strategy: StrategyMode
