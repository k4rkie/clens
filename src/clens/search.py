from pathlib import Path
from PIL import Image, UnidentifiedImageError
from clens.exceptions import InvalidImageError


def find_images(query_text: str, count: int):
    from clens.embedder import embed_text
    from clens.data_store import get_chroma_client, retrieve_images

    query_text_embd = embed_text(query_text)
    chroma_client = get_chroma_client()

    return retrieve_images(query_text_embd, chroma_client, count)


def match_images(img_path: Path, count: int):
    from clens.embedder import embed_image
    from clens.data_store import get_chroma_client, retrieve_images
    from PIL import Image

    try:
        image_data = Image.open(img_path)
        image_embedding = embed_image(image_data)
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError(
            f"Could not read the provided image (it may be corrupted or unsupported): {img_path}"
        ) from exc

    chroma_client = get_chroma_client()

    return retrieve_images(image_embedding, chroma_client, count)
