from pydantic import BaseModel
from enum import StrEnum

from config import settings

class Collections(StrEnum):
    """
    исходя из выбранной коллекции ожидается определенная структура документа который будет векторизироваться
    """
    base = settings.vdb.base_collection
    questions = settings.vdb.questions_collection

class ParamsVectorization(BaseModel):
    collection: Collections

class ResponseVectorization(BaseModel):
    count_vectors: int