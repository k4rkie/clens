from fastapi import FastAPI, Response, status
from contextlib import asynccontextmanager
from clens.data_schemas import IndexDirData, ResponseBody
import logging
from clens.embedder import get_model
from clens.data_store import get_chroma_client
import asyncio
from clens.runtime import RuntimeState
from chromadb.errors import NotFoundError as ChromaNotFoundError
import os
from clens.logger_config import configure_logging

runtime_state = RuntimeState().load_runtime()
configure_logging(server=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    runtime_state.active_host = os.environ.get("CLENS_RUNTIME_HOST")
    runtime_state.active_port = os.environ.get("CLENS_RUNTIME_PORT")
    runtime_state.pid = os.getpid()
    runtime_state.save_runtime()
    await asyncio.to_thread(get_model)
    get_chroma_client()
    yield
    runtime_state.clear_runtime()


clens_server = FastAPI(lifespan=lifespan)

logger = logging.getLogger(__name__)


@clens_server.get("/api/health", response_model=ResponseBody)
def health():
    return ResponseBody(message="Status OK")


@clens_server.post("/api/index", response_model=ResponseBody)
def index_dir(req: IndexDirData, response: Response):
    from clens.indexer import index_images

    logger.info("Indexing directory: %s", req.path)
    try:
        index_images(req.path)
        logger.info("Finished indexing directory: %s", req.path)
        return ResponseBody(message=f"The directory {req.path} has been indexed")
    except NotADirectoryError as exc:
        logger.warning("Index path is not a directory: %s", req.path)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ResponseBody(message=str(exc), error_type="NotADirectoryError")
    except FileNotFoundError as exc:
        logger.warning("Index directory does not exist: %s", req.path)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ResponseBody(message=str(exc), error_type="FileNotFoundError")
    except Exception:
        logger.exception("Unexpected error while indexing directory: %s", req.path)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ResponseBody(
            message="Something went wrong while indexing the directory",
            error_type="InternalServerError",
        )


@clens_server.get("/api/find/{query_term}", response_model=ResponseBody)
def find_image(query_term: str, response: Response, count: int = 5):
    from clens.search import find_images

    logger.info("Searching for query: %s (count=%d)", query_term, count)
    try:
        result = find_images(query_term, count)
        logger.info("Finished search for query: %s", query_term)
        return ResponseBody(message=f"Found results for {query_term}", body=result)
    except ChromaNotFoundError:
        logger.warning("Search requested before any images were indexed")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ResponseBody(
            message="Seems like you have no indexed directories",
            error_type="ChromaNotFoundError",
        )
    except Exception:
        logger.exception("Unexpected error while searching for query: %s", query_term)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ResponseBody(
            message="Something went wrong while searching",
            error_type="InternalServerError",
        )


@clens_server.get("/api/match", response_model=ResponseBody)
def match_image(image_path: str, response: Response, count: int = 5):
    from clens.search import match_images
    from pathlib import Path

    logger.info("Matching image: %s (count=%d)", image_path, count)
    try:
        result = match_images(Path(image_path).absolute(), count)
        logger.info("Finished matching image: %s", image_path)
        return ResponseBody(
            message=f"Found matches for {os.path.basename(image_path)}", body=result
        )
    except ChromaNotFoundError:
        logger.warning("Image match requested before any images were indexed")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ResponseBody(
            message="Seems like you have no indexed directories",
            error_type="ChromaNotFoundError",
        )
    except Exception:
        logger.exception("Unexpected error while matching image: %s", image_path)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ResponseBody(
            message="Something went wrong while matching the image",
            error_type="InternalServerError",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        clens_server,
        host=os.environ["CLENS_RUNTIME_HOST"],
        port=int(os.environ["CLENS_RUNTIME_PORT"]),
        log_level="info",
        access_log=False,
        log_config=None,
    )
