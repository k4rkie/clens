def find_images(query_text: str, count: int):
    from clens.embedder import embed_text
    from clens.data_store import get_chroma_client, retrieve_images

    query_text_embd = embed_text(query_text)
    chroma_client = get_chroma_client()

    return retrieve_images(query_text_embd, chroma_client, count)
