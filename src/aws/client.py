from typing import AsyncGenerator
from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession

from config import settings


async def get_aws_client() -> AsyncGenerator[AioBaseClient, None]:
    session = AioSession()

    async with session.create_client(
        "s3",
        aws_access_key_id=settings.aws.access_key,
        aws_secret_access_key=settings.aws.secret_key,
        endpoint_url=settings.aws.endpoint,
        verify=False
    ) as client:
        yield client
