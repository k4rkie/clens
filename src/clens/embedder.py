from pathlib import Path
from filetype import guess_mime
import uuid
import hashlib
from numpy.typing import NDArray
import numpy as np
from clens.data_schemas import ImageData, Candidate

CLIP_MODEL = "clip-ViT-B-32"
_model = None


def get_model():
    from sentence_transformers import SentenceTransformer

    global _model
    if _model is None:
        try:
            _model = SentenceTransformer(CLIP_MODEL, local_files_only=True)
        except Exception:
            _model = SentenceTransformer(CLIP_MODEL)
    return _model


def embed_image(image_data) -> NDArray[np.float32]:

    model = get_model()
    return model.encode(image_data, normalize_embeddings=True)


def generate_image_hash(image_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(image_path, "rb") as img:
        while chunk := img.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def embed_images(files: list[Path]) -> list[ImageData]:
    from clens.data_store import filter_preexisting_images, get_chroma_client

    candidates: list[Candidate] = []
    for file in files:
        image_hash = generate_image_hash(file)
        candidates.append({"id": image_hash, "path": file})

    chroma_client = get_chroma_client()

    new_images = filter_preexisting_images(chroma_client, candidates)

    if len(new_images) == 0:
        return []

    embedded: list[ImageData] = []
    for candidate in new_images:
        from PIL import Image

        pil_image = Image.open(candidate["path"])
        embedding = embed_image(pil_image)
        embedded.append(
            {
                "id": candidate["id"],
                "file_type": guess_mime(candidate["path"]),
                "path": candidate["path"],
                "embedding": embedding,
            }
        )
    return embedded


def embed_text(query_text: str) -> NDArray[np.float32]:
    model = get_model()

    return model.encode(query_text, normalize_embeddings=True)
