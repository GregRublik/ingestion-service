import tempfile

from aiobotocore.response import StreamingBody

from repositories.document import DocumentRepository
from repositories.aws import AWSRepository
from services.unit_of_work import UnitOfWork
from config import settings
from models.document import Document

from docling.document_converter import DocumentConverter


import json
import asyncio
import re
from pathlib import Path
from typing import Callable, Awaitable


class NormalizationService:

    def __init__(
        self,
        aws_repository: AWSRepository,
        document_repository: DocumentRepository,
        uow: UnitOfWork
    ) -> None:
        self.document_repository = document_repository
        self.aws_repository = aws_repository
        self.uow = uow

        self.parsers: dict[str, Callable[[any], Awaitable[dict]]] = {
            ".pdf": self.normalize_with_docling,
            ".png": self.normalize_with_docling,
            ".jpg": self.normalize_with_docling,
            ".jpeg": self.normalize_with_docling,
            ".docx": self.normalize_with_docling,

            ".json": self.normalize_json,
            ".txt": self.normalize_text,
        }

        self.converter = DocumentConverter()

    # ========================
    # PUBLIC API
    # ========================

    async def normalize_document(self, doc_id: int):
        async with self.uow:
            document_db = await self.document_repository.get_by_id(
                self.uow.session, doc_id
            )

            try:
                # 1. статус
                document_db.status = document_db.status.PROCESSING


                file_obj = await self.aws_repository.get_document(
                    settings.aws.bucket_name, document_db.file_name
                )

                content: StreamingBody = file_obj["body"]

                # 3. парсер
                parser = self.parsers.get(document_db.file_extension.lower())

                if not parser:
                    raise ValueError(
                        f"Unsupported file type: {document_db.file_extension}"
                    )

                # 4. нормализация
                normalized = await parser(content)

                # 5. сохранение
                normalized_path = await self.save_normalized(
                    document_db, normalized
                )

                # 6. мета
                document_db.meta = {
                    **(document_db.meta or {}),
                    "normalized_path": normalized_path,
                    "normalized": True,
                }

                document_db.status = document_db.status.NORMALIZED

                return document_db

            except Exception as e:
                document_db.status = document_db.status.FAILED
                document_db.error_message = str(e)
                return document_db

    # ========================
    # TEXT / JSON
    # ========================

    @staticmethod
    async def normalize_text(content: bytes) -> dict:
        text = content.decode("utf-8", errors="ignore")
        text = NormalizationService._clean_text(text)

        paragraphs = [
            p.strip() for p in text.split("\n\n") if p.strip()
        ]

        return {
            "type": "text",
            "content": text,
            "structure": [
                {"type": "paragraph", "text": p} for p in paragraphs
            ],
            "metadata": {
                "paragraphs": len(paragraphs)
            },
        }

    @staticmethod
    async def normalize_json(content: bytes) -> dict:
        data = json.loads(content.decode("utf-8"))

        entries = []

        def flatten(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    flatten(v, f"{path}.{k}" if path else k)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    flatten(v, f"{path}[{i}]")
            else:
                entries.append({
                    "path": path,
                    "value": str(obj)
                })

        flatten(data)

        content_text = "\n".join(
            f"{e['path']}: {e['value']}" for e in entries
        )

        return {
            "type": "json",
            "content": content_text,
            "structure": entries,
            "metadata": {
                "entries": len(entries)
            }
        }

    # ========================
    # DOCLING (CPU-bound → thread pool)
    # ========================

    async def normalize_with_docling(self, streaming_body) -> dict:
        loop = asyncio.get_running_loop()

        import os
        tmp = tempfile.NamedTemporaryFile(delete=False)

        try:
            # читаем поток
            while chunk := await streaming_body.read(1024 * 1024):
                tmp.write(chunk)

            tmp.flush()
            tmp.close()

            return await loop.run_in_executor(
                None,
                self._normalize_with_docling_sync,
                tmp.name
            )

        finally:
            try:
                await streaming_body.close()
            except Exception:
                print("error close streaming body")

            try:
                os.unlink(tmp.name)
            except Exception:
                pass


    def _normalize_with_docling_sync(self, file_path: str) -> dict:
        """
        file_stream — это file-like объект (например StreamingBody из S3)
        """
        doc = self.converter.convert(file_path)

        blocks = []
        full_text = []

        for block in getattr(doc, "blocks", []):
            text = self._clean_text(getattr(block, "text", "") or "")

            if not text:
                continue

            blocks.append({
                "type": getattr(block, "type", "unknown"),
                "text": text,
                "bbox": getattr(block, "bbox", None),
                "page": getattr(block, "page_number", None),
            })

            full_text.append(text)

        return {
            "type": "docling",
            "content": "\n".join(full_text),
            "structure": blocks,
            "metadata": {
                "blocks": len(blocks),
                "pages": getattr(doc, "num_pages", None)
            }
        }

    # ========================
    # SAVE
    # ========================

    async def save_normalized(
        self,
        parent_doc: Document,
        normalized_data: dict
    ) -> str:
        filename = Path(parent_doc.file_name).stem
        key = f"normalized/{filename}.json"

        payload = json.dumps(normalized_data, ensure_ascii=False).encode("utf-8")

        await self.aws_repository.push_document(
            settings.aws.bucket_name,
            key,
            payload
        )

        await self.document_repository.add_one(self.uow.session,{
                    "file_name": f"{filename}.json",
                    "file_type": "application/json",
                    "file_extension": ".json",
                    "file_size": len(payload),
                    "storage_path": f"s3://{settings.aws.bucket_name}/{key}",
                    "status": parent_doc.status.NORMALIZED,
                })

        return key

    # ========================
    # UTILS
    # ========================

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()
