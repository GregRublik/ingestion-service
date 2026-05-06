import tempfile

from aiobotocore.response import StreamingBody

from repositories.document import DocumentRepository
from repositories.aws import AWSRepository
from services.unit_of_work import UnitOfWork
from config import settings
from models.document import Document, DocumentStatus
from schemas.document import ParamsNormalize, StrategyMode

from docling.document_converter import DocumentConverter
from docling.datamodel.document import DocumentStream
from io import BytesIO


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

        self.parsers = {
            ".pdf": self.normalize_with_docling,
            ".png": self.normalize_with_docling,
            ".jpg": self.normalize_with_docling,
            ".jpeg": self.normalize_with_docling,
            ".docx": self.normalize_with_docling,

            ".json": self.normalize_json,
            ".txt": self.normalize_text,
        }

        self.converter = DocumentConverter()

    def get_handler_normalization(self, file_extension):

        handler = self.parsers[file_extension]

        return handler

    # ========================
    # PUBLIC API
    # ========================

    async def normalize_document(self, doc_id: int, params_normalize: ParamsNormalize):
        async with self.uow:
            document_db = await self.document_repository.get_by_id(
                self.uow.session, doc_id
            )

            try:
                # 1. статус
                document_db.status = DocumentStatus.PROCESSING


                file_obj = await self.aws_repository.get_document(
                    settings.aws.bucket_name, document_db.file_name
                )

                content: StreamingBody = file_obj["body"]
                cont = await content.read()

                handler = self.get_handler_normalization(document_db.file_extension)

                result = await handler(cont, params_normalize)

                return await self.save_normalized(
                    document_db, result, params_normalize
                )

                # # Создаем DocumentStream из байтов
                # doc_stream = DocumentStream(
                #     name=document_db.file_name,  # имя файла
                #     stream=BytesIO(cont)  # передаем как поток
                # )
                # result = self.converter.convert(doc_stream).document
                # print("res: ", result.export_to_markdown())
                #
                # return await self.save_normalized(
                #     document_db, result.export_to_markdown()
                # )


            except Exception as e:
                print(str(e)[::500])
                document_db.status = DocumentStatus.FAILED
                # document_db.error_message = str(e)[::500]
                return document_db

    # ========================
    # TEXT / JSON
    # ========================

    @staticmethod
    async def normalize_text(content: bytes, params_normalize: ParamsNormalize) -> dict:
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
    async def normalize_json(content: bytes, params_normalize: ParamsNormalize):
        data = json.loads(content.decode("utf-8"))

        if params_normalize.strategy == StrategyMode.questions_and_answers:
            normalized_questions = []
            questions = data["data"]["questions"]
            for question in questions:

                normalized_questions.append(
                    {
                        "question": question["text"],
                        "answer": question["answer"]["text"],
                        "imt_id": question["productDetails"]["imtId"],
                        "nm_id": question["productDetails"]["nmId"],
                        "product_name": question["productDetails"]["productName"]
                    }
                )

            return {"results": normalized_questions}

        return data

    async def normalize_with_docling(self, streaming_body, strategy: ParamsNormalize) -> dict:
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
                streaming_body.close()
            except Exception as e:
                print(f"error close streaming body{e}")

            try:
                os.unlink(tmp.name)
            except Exception as e:
                print(f"error os.unlink {e}")



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
        normalized_data,
        params_normalize: ParamsNormalize
    ) -> str:

        filename = Path(parent_doc.file_name).stem

        if params_normalize.strategy == StrategyMode.questions_and_answers:
            key = f"normalized/{filename}.json"
            payload = normalized_data
            file_extension = ".json"
            file_type = "application/json"
        else:

            key = f"normalized/{filename}.md"
            payload = normalized_data
            file_extension = ".md"
            file_type = "text/markdown"

        await self.aws_repository.push_document(
            settings.aws.bucket_name,
            key,
            payload
        )

        document_db = await self.document_repository.add_one(self.uow.session,{
                    "file_name": f"{filename}{file_extension}",
                    "file_type": file_type,
                    "file_extension": file_extension,
                    "file_size": len(payload),
                    "storage_path": f"s3://{settings.aws.bucket_name}/{key}",
                    "status": DocumentStatus.NORMALIZED,
                })

        return document_db

    # ========================
    # UTILS
    # ========================

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()
