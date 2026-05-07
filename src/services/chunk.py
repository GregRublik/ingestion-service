from aiobotocore.response import StreamingBody
from langchain_experimental.text_splitter import SemanticChunker

from models.document import Document, DocumentStatus
from repositories.aws import AWSRepository
from typing import Literal
from pathlib import Path
import json

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from config import settings
from repositories.document import DocumentRepository
from schemas.chunk import ChunkType
from services.embedding import EmbeddingService
from services.unit_of_work import UnitOfWork


class ChunkService:

    def __init__(
            self,
        aws_repository: AWSRepository,
        document_repository: DocumentRepository,
        uow: UnitOfWork,
        embedding_service: EmbeddingService,
    ):
        self.aws_repository = aws_repository
        self.document_repository = document_repository
        self.uow = uow
        self.embedding_service = embedding_service

    chunking_methods = {
        "recursive": RecursiveCharacterTextSplitter,
        "char": CharacterTextSplitter,
        "markdown": MarkdownHeaderTextSplitter,
        "semantic": SemanticChunker
    }

    def _get_splitter(self, chunk_type: str, params: dict, embedding):
        if chunk_type == "semantic":
            return self.chunking_methods[chunk_type](**params, embeddings=embedding)
        return self.chunking_methods[chunk_type](**params)

    async def chunk(
            self,
            doc: Document,
            chunk_type: ChunkType,
            params: dict
    ):

        file_obj = await self.aws_repository.get_document(
            settings.aws.bucket_name,
            f"normalized/{doc.file_name}"
        )

        content: StreamingBody = file_obj["body"]
        cont = await content.read()

        text = cont.decode("utf-8", errors="ignore")  # ✅ важно
        print(text[:100:])
        if chunk_type == ChunkType.questions_and_answers:
            # questions_and_answers = json.dumps(text, ensure_ascii=False).encode("utf-8")
            questions_and_answers = json.loads(text)
            chunks = [
                {
                    "id": i,
                    "question": question_and_answer.get("question"),
                    "answer": question_and_answer.get("answer"),
                    "product_name": question_and_answer.get("product_name"),
                    "product_id": question_and_answer.get("imt_id"), # todo либо nm_id
                    "metadata": {
                        "chunk_index": i,
                        "length": len(question_and_answer)
                    }
                }
                for i, question_and_answer in enumerate(questions_and_answers["results"])
            ]
            return {
                "chunks": chunks,
                "meta": {
                    "chunk_type": chunk_type,
                    "params": params
                }
            }
        else:

            splitter = self._get_splitter(chunk_type, params, self.embedding_service.model)

            raw_chunks = splitter.split_text(text)

            chunks = [
                {
                    "id": i,
                    "text": chunk,
                    "metadata": {
                        "chunk_index": i,
                        "length": len(chunk)
                    }
                }
                for i, chunk in enumerate(raw_chunks)
            ]

            return {
                "chunks": chunks,
                "meta": {
                    "chunk_type": chunk_type,
                    "params": params
                }
            }

    async def save_chunks(
            self,
            parent_doc: Document,
            chunk_data: dict,
            chunk_type: str
    ) -> Document:
        filename = Path(parent_doc.file_name).stem
        key = f"chunks/{chunk_type}/chunks-{filename}.json"

        payload = json.dumps(chunk_data, ensure_ascii=False).encode("utf-8")

        await self.aws_repository.push_document(
            settings.aws.bucket_name,
            key,
            payload
        )

        return await self.document_repository.add_one(
            self.uow.session,
            {
                "file_name": f"chunks-{filename}.json",
                "file_type": "application/json",
                "file_extension": ".json",
                "file_size": len(payload),
                "storage_path": f"s3://{settings.aws.bucket_name}/{key}",
                "status": DocumentStatus.EMBEDDING,  # следующий этап
            }
        )


    async def chunk_document(
            self,
            doc_id: int,
            chunk_type: ChunkType,
            params: dict
    ) -> Document:
        async with self.uow:
            document = await self.document_repository.get_by_id(
                self.uow.session,
                doc_id
            )

            try:
                document.status = DocumentStatus.PROCESSING

                chunk_data = await self.chunk(
                    document,
                    chunk_type,
                    params
                )

                db_document = await self.save_chunks(
                    document,
                    chunk_data,
                    chunk_type
                )

                document.status = DocumentStatus.EMBEDDING

                return db_document

            except Exception as e:
                document.status = DocumentStatus.FAILED
                document.error_message = str(e)
                raise e

