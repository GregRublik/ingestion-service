from aiobotocore.client import AioBaseClient
from exceptions import NoSuchBucketException


class AWSRepository:
    def __init__(self, client: AioBaseClient):
        self.client = client

    async def push_document(self, bucket: str, key: str, data: bytes):
        try:
            await self.client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
            )
        except self.client.exceptions.NoSuchBucket:
            raise NoSuchBucketException

    async def get_document(self, bucket: str, key: str) -> dict:
        response = await self.client.get_object(
            Bucket=bucket,
            Key=key,
        )
        return {
            "body": response["Body"],
            "content_type": response.get("ContentType"),
        }

    async def delete_document(self,bucket: str, key: str):
        await self.client.delete_object(Bucket=bucket, Key=key)

    async def get_download_url(self, bucket: str, key: str) -> str:
        return await self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600,
        )