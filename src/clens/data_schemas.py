from pydantic import BaseModel


class IndexDirData(BaseModel):
    path: str


class FindImageData(BaseModel):
    query_term: str
    count: int
