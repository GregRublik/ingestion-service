from enum import StrEnum
from pydantic import BaseModel


class StrategyMode(StrEnum):
    base = "base"
    questions_and_answers = "questions_and_answers"

class ParamsNormalize(BaseModel):
    strategy: StrategyMode
