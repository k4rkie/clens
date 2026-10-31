from clens.dir_crawler import find_images
from clens.embedder import embed_images
from clens.data_store import get_chroma_client, store_image_data
from clens.exceptions import NoImagesFoundError


def index_images(root_dir: str) -> None:
    # get images recursively form the provided dir
    file_paths = find_images(root_dir)

    if len(file_paths) == 0:
        raise NoImagesFoundError(f"No supported images found in: {root_dir}")

    # generate embeddings from images
    image_data = embed_images(file_paths)

    if len(image_data) == 0:
        return

    # get the shared chroma client
    chroma_client = get_chroma_client()

    # store the embeddings in chroma db
    store_image_data(chroma_client, image_data)
