from clens.dir_crawler import find_images
from clens.embedder import embed_images
from clens.data_store import init_chroma_client, store_image_data


def index_files(root_dir: str) -> None:
    file_paths = find_images(root_dir)
    image_data = embed_images(file_paths)
    chroma_client = init_chroma_client("./.chroma_store")
    store_image_data(chroma_client, image_data)
