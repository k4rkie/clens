from fastapi import FastAPI, HTTPException, Response, status
from clens.data_schemas import (
    IndexDirData,
    ResponseBody,
)
import logging

logging.basicConfig(
    level=logging.WARNING, format=" [%(levelname)s] %(name)s: %(message)s", force=True
)

logger = logging.getLogger(__name__)

clens_server = FastAPI()


@clens_server.get("/api/health", response_model=ResponseBody)
def health():
    return ResponseBody(message="Status OK")


@clens_server.post("/api/index", response_model=ResponseBody)
def index_dir(req: IndexDirData, response: Response):
    from clens.indexer import index_images

    try:
        index_images(req.path)
        return ResponseBody(message=f"The directory {req.path} has been indexed")
    except NotADirectoryError as NAD:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ResponseBody(message=f"{NAD}")
    except FileNotFoundError as FNF:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ResponseBody(message=f"{FNF}")


@clens_server.get("/api/find/{query_term}", response_model=ResponseBody)
def find_image(query_term: str, response: Response, count: int = 5):
    from clens.search import find_images

    try:
        result = find_images(query_term, count)
        return ResponseBody(message=f"Found images for {query_term}", body=result)
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ResponseBody(message=f"Something went wrong")
