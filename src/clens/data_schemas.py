from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class IndexDirData(BaseModel):
    path: str


class ResponseBody(BaseModel, Generic[T]):
    message: str
    body: T | None = None
