from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel
from datetime import datetime

T = TypeVar("T")


class APIResponse(GenericModel, Generic[T]):
    success: bool = True
    date: datetime = datetime.now()
    data: Optional[T] = None
    error: Optional[str] = None


def ok(data):
    return APIResponse(data=data)
