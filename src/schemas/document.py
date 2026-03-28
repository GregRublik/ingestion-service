from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional, Dict

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
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
