from clens.dir_crawler import find_images
from clens.embedder import embed_images
from clens.data_store import get_chroma_client, store_image_data


def index_images(root_dir: str) -> None:
    # get images recursively form the provided dir
    file_paths = find_images(root_dir)

    # generate embeddings from images
    image_data = embed_images(file_paths)

    # get the shared chroma client
    chroma_client = get_chroma_client()

    # store the embeddings in chroma db
    store_image_data(chroma_client, image_data)
