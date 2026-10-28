from pydantic import BaseModel
from pathlib import Path
from typing import Generic, TypeVar, TypedDict
from numpy.typing import NDArray
import numpy as np

T = TypeVar("T")


class IndexDirData(BaseModel):
    path: str


class ResponseBody(BaseModel, Generic[T]):
    message: str
    body: T | None = None
    error_type: str | None = None


class ImageData(TypedDict):
    id: str
    file_type: str
    path: Path
    embedding: NDArray[np.float32]


class Candidate(TypedDict):
    id: str
    path: Path
