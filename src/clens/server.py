from fastapi import FastAPI
from clens.indexer import index_files
from clens.search import search_images

clens_server = FastAPI()


@clens_server.get("/api/health")
def health():
    return {"Status": "OK"}


@clens_server.post("/index")
def index_dir(dir: str):
    try:
        index_files(dir)
        return {"path": dir}
    except:
        pass


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
