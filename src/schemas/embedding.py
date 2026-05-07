from pydantic import BaseModel
from enum import StrEnum

from config import settings

class Collections(StrEnum):
    base = settings.vdb.base_collection
    questions = settings.vdb.questions_collection

class VectorStrategy(StrEnum):
    base = "base"
    question_answer = "question_answer"

class ParamsVectorization(BaseModel):
    collection: Collections
    strategy: VectorStrategy
