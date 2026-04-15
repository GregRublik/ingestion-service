from aiobotocore.client import AioBaseClient
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.document import DocumentRepository
from services import document, unit_of_work
from repositories.aws import AWSRepository
from aws.client import get_aws_client
from db.database import get_db_session
from services.chunk import ChunkService
from services.normalization import NormalizationService


# REPOSITORIES
def get_aws_repository(
    client: AioBaseClient = Depends(get_aws_client),
) -> AWSRepository:
    return AWSRepository(client)

def get_document_repository() -> DocumentRepository:
    return DocumentRepository()

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

def get_chunk_service(
    aws_repository: AWSRepository = Depends(get_aws_repository),
) -> ChunkService:
    return ChunkService(aws_repository)
