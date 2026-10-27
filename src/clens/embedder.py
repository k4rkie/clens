from pathlib import Path
from filetype import guess_mime
from typing import TypedDict
import uuid

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


class ImageData(TypedDict):
    id: uuid.UUID
    file_type: str
    path: Path
    embedding: list[float]


def embed_images(files: list[Path]) -> list[ImageData]:
    from PIL import Image

    model = get_model()
    image_data = []

    for file in files:
        image = Image.open(file)
        image_embedding = model.encode(image, normalize_embeddings=True)
        image_data.append(
            {
                "id": uuid.uuid4(),
                "file_type": guess_mime(file),
                "path": file,
                "embedding": image_embedding,
            }
        )
    return image_data


def embed_text(query_text: str):
    model = get_model()

    return model.encode(query_text, normalize_embeddings=True)
