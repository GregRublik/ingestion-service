from aiobotocore.client import AioBaseClient
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client import AsyncQdrantClient

from config import settings

from repositories.document import DocumentRepository
from repositories.qdrant import QdrantRepository
from repositories.aws import AWSRepository

from services import document, unit_of_work
from services.chunk import ChunkService
from services.normalization import NormalizationService
from services import embedding

from aws.client import get_aws_client
from db.database import get_db_session


def get_vectordb_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(
        url=f"http://{settings.vdb.host}:{settings.vdb.port}",
    )

# REPOSITORIES
def get_aws_repository(
    client: AioBaseClient = Depends(get_aws_client),
) -> AWSRepository:
    return AWSRepository(client)

def get_document_repository() -> DocumentRepository:
    return DocumentRepository()

def get_qdrant_repository(
        client: AsyncQdrantClient = Depends(get_vectordb_client)
) -> QdrantRepository:
    return QdrantRepository(
        client,
        settings.vdb.base_collection
    )

# SERVICES
def get_uow_service(
    session: AsyncSession = Depends(get_db_session),
) -> unit_of_work.UnitOfWork:
    return unit_of_work.UnitOfWork(session)

def get_document_service(
    aws_repository: AWSRepository = Depends(get_aws_repository),
    document_repository: DocumentRepository = Depends(get_document_repository),
    uow: unit_of_work.UnitOfWork = Depends(get_uow_service),
) -> document.DocumentService:
    return document.DocumentService(aws_repository, document_repository, uow)

def get_normalization_service(
    aws_repository: AWSRepository = Depends(get_aws_repository),
    document_repository: DocumentRepository = Depends(get_document_repository),
    uow: unit_of_work.UnitOfWork = Depends(get_uow_service),
) -> NormalizationService:
    return NormalizationService(aws_repository, document_repository, uow)

def get_embedding_service(
    document_repository: DocumentRepository = Depends(get_document_repository),
    aws_repository: AWSRepository = Depends(get_aws_repository),
    qdrant_repository: QdrantRepository = Depends(get_qdrant_repository),
    uow: unit_of_work.UnitOfWork = Depends(get_uow_service),
):
    return embedding.EmbeddingService(document_repository, aws_repository, qdrant_repository, uow)

def get_chunk_service(
    aws_repository: AWSRepository = Depends(get_aws_repository),
    document_repository: DocumentRepository = Depends(get_document_repository),
    uow: unit_of_work.UnitOfWork = Depends(get_uow_service),
    embedding_service: embedding.EmbeddingService = Depends(get_embedding_service),
) -> ChunkService:
    return ChunkService(aws_repository, document_repository, uow, embedding_service)
