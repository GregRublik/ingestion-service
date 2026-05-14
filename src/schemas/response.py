from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel

T = TypeVar("T")


class APIResponse(GenericModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
