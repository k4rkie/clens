from pydantic import BaseModel
from typing import Optional, Generic, TypeVar

T = TypeVar("T")


class IndexDirData(BaseModel):
    path: str


class ResponseBody(BaseModel, Generic[T]):
    message: str
    body: Optional[T] = None
