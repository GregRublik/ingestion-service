from pydantic import BaseModel
from typing import Literal, Dict, Any
from enum import StrEnum


class ChunkType(StrEnum):
    recursive = 'recursive'
    char = 'char'
    markdown = 'markdown'
    semantic = 'semantic'

class ChunkRequest(BaseModel):
    chunk_type: ChunkType
    params: Dict[str, Any] = {}
