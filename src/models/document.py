from datetime import datetime, timezone
import enum

from sqlalchemy import Column, Integer, Enum, String, JSON, DateTime, func

from db.database import Base


class DocumentStatus(enum.Enum):
    UPLOADED = "uploaded"  # приняли документ
    PROCESSING = "processing"  # идёт обработка
    NORMALIZED = "normalized" # нормализован
    EMBEDDING = "embedding"  # считаются embeddings
    INDEXING = "indexing"  # пишем в vector DB
    READY = "ready"  # готов к использованию
    FAILED = "failed"  # ошибка
    DELETED = "deleted"  # удалён

class Document(Base):
    __tablename__ = 'ingestion_documents'

    id = Column(Integer, primary_key=True)
    version = Column(Integer, default=1)

    status = Column(
        Enum(DocumentStatus, name="document_status"),
        default=DocumentStatus.UPLOADED,
        nullable=False
    )

    storage_path = Column(String, nullable=True)  # s3://...
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)  # pdf, txt
    file_extension = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)

    meta = Column(JSON, default={})

    error_message = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Database sets the time on creation
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=datetime.now(timezone.utc),  # Python sets the time on update
        server_default=func.now(),  # Database sets initial time on creation
        nullable=False
    )
