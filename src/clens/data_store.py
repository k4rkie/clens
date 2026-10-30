from typing import TYPE_CHECKING
from clens.paths import STORE_DIR
from clens.data_schemas import Candidate

if TYPE_CHECKING:
    from chromadb.api import ClientAPI
    from chromadb.api.types import QueryResult
    from clens.embedder import ImageData
    from pathlib import Path


_chroma_client = None


def get_chroma_client() -> ClientAPI:
    from chromadb import PersistentClient

    global _chroma_client
    if _chroma_client is None:
        _chroma_client = PersistentClient(path=STORE_DIR)
    return _chroma_client


def filter_preexisting_images(
    client: ClientAPI, candidates: dict[str, Path]
) -> list[dict[str, Path]]:
    image_collection = client.get_or_create_collection(
        "image_data", configuration={"hnsw": {"space": "cosine"}}
    )

    existing_ids: set[str] = set(
        image_collection.get(ids=[id for id in candidates.keys()])["ids"]
    )

    if len(existing_ids) == 0:
        return candidates

    return [id for id in candidates.keys() if id not in existing_ids]


def store_image_data(client: ClientAPI, image_data: list[ImageData]) -> None:
    image_collection = client.get_or_create_collection(
        "image_data", configuration={"hnsw": {"space": "cosine"}}
    )
    image_collection.add(
        ids=[str(data["id"]) for data in image_data],
        embeddings=[data["embedding"] for data in image_data],
        metadatas=[
            {"file_type": str(data["file_type"]), "path": str(data["path"])}
            for data in image_data
        ],
    )


def retrieve_images(embedding, client: ClientAPI, result_count: int) -> QueryResult:
    image_collection = client.get_collection("image_data")
    return image_collection.query(query_embeddings=embedding, n_results=result_count)
