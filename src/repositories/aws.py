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
            return {"id": 123, "storage_path": f"s3://{bucket}/{key}"}
        except self.client.exceptions.NoSuchBucket:
            raise NoSuchBucketException

    async def get_document(self, bucket: str, key: str):
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