from pydantic import BaseModel
from typing import Literal, Dict, Any


class ChunkRequest(BaseModel):
    chunk_type: Literal["recursive", "char", "markdown", "semantic"]
    params: Dict[str, Any] = {}