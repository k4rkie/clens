from pathlib import Path
from filetype import guess_mime
from typing import TypedDict
import uuid


class ImageData(TypedDict):
    id: uuid.UUID
    file_type: str
    path: Path
    embedding: list[float]


def embed_images(files: list[Path]) -> list[ImageData]:
    from sentence_transformers import SentenceTransformer
    from PIL import Image

    model = SentenceTransformer("clip-ViT-B-32")
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
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("clip-ViT-B-32")

    return model.encode(query_text, normalize_embeddings=True)
