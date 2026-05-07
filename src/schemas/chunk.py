from pydantic import BaseModel
from typing import Literal, Dict, Any
from enum import StrEnum
from config import settings


class ChunkType(StrEnum):
    recursive = 'recursive'
    char = 'char'
    markdown = 'markdown'
    semantic = 'semantic'
    questions = settings.vdb.questions_collection

class ChunkRequest(BaseModel):
    chunk_type: ChunkType
    params: Dict[str, Any] = {}
