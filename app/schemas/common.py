from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PageResult(BaseModel, Generic[T]):
    total: int
    items: List[T]

    class Config:
        from_attributes = True
