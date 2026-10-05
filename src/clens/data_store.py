from typing import TYPE_CHECKING, Collection

if TYPE_CHECKING:
    from chromadb.api import ClientAPI
    from chromadb.api.types import QueryResult
    from clens.embedder import ImageData


def init_chroma_client(store_path: str) -> ClientAPI:
    from chromadb import PersistentClient

    return PersistentClient(path=store_path)


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


def retrieve_images(embedding, client: ClientAPI, result_count=5) -> QueryResult:
    image_collection = client.get_collection("image_data")
    return image_collection.query(query_embeddings=embedding, n_results=result_count)
