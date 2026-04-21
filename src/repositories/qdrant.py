from qdrant_client import AsyncQdrantClient

# client = AsyncQdrantClient(url="http://localhost:6333")
# await client.create_collection(...)

class QdrantRepository:

    def __init__(self, client: AsyncQdrantClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name

    async def upsert(self, points: list[dict]):
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
