from pydantic import BaseModel
from enum import StrEnum

from config import settings

class Buckets(StrEnum):
    base = settings.aws.base_bucket
    questions = settings.aws.questions_bucket

class VectorStrategy(StrEnum):
    base = "base"
    question_answer = "question_answer"

class ParamsVectorization(BaseModel):
    bucket: Buckets
    strategy: VectorStrategy
