from fastapi import FastAPI, HTTPException
from clens.indexer import index_images
from clens.search import search_images
from clens.data_schemas import IndexDirData
import logging

logging.basicConfig(
    level=logging.WARNING, format=" [%(levelname)s] %(name)s: %(message)s", force=True
)

logger = logging.getLogger(__name__)

clens_server = FastAPI()


@clens_server.get("/api/health")
def health():
    return {"Status": "OK"}


@clens_server.post("/api/index")
def index_dir(req: IndexDirData):
    try:
        index_images(req.path)
        return {"message": f"The directory {req.path} has been indexed"}
    except NotADirectoryError as NAD:
        raise HTTPException(status_code=400, detail=f"{NAD}")
    except FileNotFoundError as FNF:
        raise HTTPException(status_code=400, detail=f"{FNF}")


@clens_server.post("/find")
def find_image(query_text: str):
    try:
        search_images(query_text)
    except:
        pass


@clens_server.post("/match")
def match_image(image):
    pass


@clens_server.get("/")
def get_all_images():
    pass
