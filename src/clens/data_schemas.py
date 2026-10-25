from pydantic import BaseModel


class IndexDirData(BaseModel):
    path: str
