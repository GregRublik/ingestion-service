from aiobotocore.response import StreamingBody
from langchain_core.embeddings import Embeddings

from repositories.aws import AWSRepository
from repositories.document import DocumentRepository
from repositories.qdrant import QdrantRepository
from services.unit_of_work import UnitOfWork
from models.document import DocumentStatus
from config import settings
import json


class EmbeddingService:

    def __init__(
        self,
        model,
        document_repository: DocumentRepository,
        aws_repository: AWSRepository,
        qdrant_repository: QdrantRepository,
        uow: UnitOfWork
    ):
        self.model = model
        self.document_repository = document_repository
        self.aws_repository = aws_repository
        self.qdrant_repository = qdrant_repository
        self.uow = uow

    def get_embedding(self) -> Embeddings:
        return self.model

    async def embedding_document(self, doc_id: int):

        async with self.uow:
            document = await self.document_repository.get_by_id(
                self.uow.session,
                doc_id
            )

            try:
                # 1. загрузка чанков
                file_obj = await self.aws_repository.get_document(
                    settings.aws.bucket_name,
                    f"chunks/semantic/{document.file_name}"
                )

                content: StreamingBody = file_obj["body"]
                raw = await content.read()

                chunk_data = json.loads(raw)

                chunks = chunk_data["chunks"]

                # 2. считаем эмбеддинги
                texts = [chunk["text"] for chunk in chunks]

                vectors = await self.model.aembed_documents(texts)

                # 3. готовим точки для Qdrant
                points = []
                c = 0
                for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                    c += 1
                    points.append({
                        "id": i,
                        "vector": vector,
                        "payload": {
                            "text": chunk["text"],
                            "doc_id": doc_id,
                            "metadata": chunk["metadata"],
                        }
                    })

                # 4. сохраняем в Qdrant
                await self.qdrant_repository.upsert(points)

                return {"status": "ok", "vectors": len(points)}

            except Exception as e:
                document.status = DocumentStatus.FAILED
                document.error_message = str(e)
                raise e