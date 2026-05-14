from aiobotocore.response import StreamingBody
from langchain_core.embeddings import Embeddings
import asyncio

from repositories.aws import AWSRepository
from repositories.document import DocumentRepository
from repositories.qdrant import QdrantRepository

from schemas.embedding import ParamsVectorization, Collections, ResponseVectorization
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

    async def create_vectors(self, field_vector: str, elements: list[dict]):
        texts = []
        for element in elements:
            texts.append(element[field_vector])
        return await self.model.aembed_documents(texts)

    async def get_chunks(self, collection: str, file_name: str):
        # 1. загрузка чанков
        file_obj = await self.aws_repository.get_document(
            settings.aws.bucket_name,
            f"chunks/{collection}/{file_name}"
        )

        content: StreamingBody = file_obj["body"]
        raw = await content.read()
        chunk_data = json.loads(raw)
        return chunk_data["chunks"]


    async def embedding_document(self, doc_id: int, params_vectorization: ParamsVectorization):

        async with self.uow:
            document = await self.document_repository.get_by_id(
                self.uow.session,
                doc_id
            )

            try:

                chunks = await self.get_chunks(params_vectorization.collection, document.file_name)

                if params_vectorization.collection == Collections.base:
                    vectors = await self.create_vectors("text", chunks)

                    # 3. готовим точки для Qdrant
                    points = []
                    c = 0
                    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                        print(vector)
                        c += 1
                        chunk["metadata"]["doc_id"] = doc_id
                        chunk["metadata"]["doc_name"] = document.file_name
                        points.append({
                            "id": i,
                            "vector": vector,
                            "payload": {
                                "text": chunk["text"],
                                "metadata": chunk["metadata"],
                            }
                        })

                    # 4. сохраняем в Qdrant
                    await self.qdrant_repository.upsert(points, params_vectorization.collection)

                    return ResponseVectorization(count_vectors=len(points))

                elif params_vectorization.collection == Collections.questions:
                    vectors = await self.create_vectors("question", chunks)


                    points = []
                    c = 0
                    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                        c += 1
                        chunk["metadata"]["doc_id"] = doc_id
                        chunk["metadata"]["doc_name"] = document.file_name
                        points.append({
                            "id": i,
                            "vector": vector,
                            "payload": {
                                "question": chunk["question"],
                                "answer": chunk["answer"],
                                "product_name": chunk["product_name"],
                                "product_id": chunk["product_id"],
                                "metadata": chunk["metadata"],
                            }
                        })

                    # 4. сохраняем в Qdrant

                    await asyncio.gather(*[
                        self.qdrant_repository.upsert(
                            points[i:i + 10],
                            params_vectorization.collection,
                        )
                        for i in range(0, len(points), 10)
                    ])
                    return ResponseVectorization(count_vectors=len(points))

            except Exception as e:
                document.status = DocumentStatus.FAILED
                document.error_message = str(e)
                raise e