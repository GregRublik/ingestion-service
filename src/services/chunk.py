from aiobotocore.response import StreamingBody
from langchain_experimental.text_splitter import SemanticChunker

from models.document import Document
from repositories.aws import AWSRepository
from typing import Literal

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from config import settings


class ChunkingService:

    def __init__(
            self,
        aws_repository: AWSRepository,
    ):
        self.aws_repository = aws_repository

    chunking_methods = {
        "recursive": RecursiveCharacterTextSplitter,
        "char": CharacterTextSplitter,
        "markdown": MarkdownHeaderTextSplitter,
        "semantic": SemanticChunker
    }

    def _get_splitter(self, chunk_type: str, params: dict):
        return self.chunking_methods[chunk_type](**params)

    async def chunk(
            self,
            doc: Document,
            chunk_type: Literal["recursive", "char", "markdown", "syntax"],
            params: dict
    ) :
        file_obj = await self.aws_repository.get_document(
            settings.aws.bucket_name, doc.file_name
        )

        splitter = self._get_splitter(chunk_type, params)

        content: StreamingBody = file_obj["body"]
        cont = await content.read()

        return splitter.split_text(cont)

