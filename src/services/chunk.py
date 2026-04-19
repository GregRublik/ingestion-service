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
            chunk_type: Literal["recursive", "char", "markdown", "semantic"],
            params: dict
    ):
        file_obj = await self.aws_repository.get_document(
            settings.aws.bucket_name,
            doc.file_name
        )

        content: StreamingBody = file_obj["body"]
        cont = await content.read()

        text = cont.decode("utf-8", errors="ignore")  # ✅ важно

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
    ) -> str:
        filename = Path(parent_doc.file_name).stem
        key = f"chunks/{chunk_type}/{filename}.json"

        payload = json.dumps(chunk_data).encode("utf-8")

        await self.aws_repository.push_document(
            settings.aws.bucket_name,
            key,
            payload
        )

        await self.document_repository.add_one(
            self.uow.session,
            {
                "file_name": f"{filename}.chunks.json",
                "file_type": "application/json",
                "file_extension": ".json",
                "file_size": len(payload),
                "storage_path": f"s3://{settings.aws.bucket_name}/{key}",
                "status": DocumentStatus.EMBEDDING,  # следующий этап
            }
        )

        return key

    async def chunk_document(
            self,
            doc_id: int,
            chunk_type: Literal["recursive", "char", "markdown", "semantic"],
            params: dict
    ):
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

                await self.save_chunks(
                    document,
                    chunk_data,
                    chunk_type
                )

                document.status = DocumentStatus.EMBEDDING

            except Exception as e:
                document.status = DocumentStatus.FAILED
                document.error_message = str(e)

