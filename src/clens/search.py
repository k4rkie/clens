def search_images(query_text: str):
    from clens.embedder import embed_text
    from clens.data_store import init_chroma_client, retrieve_images

    query_text_embd = embed_text(query_text)
    chroma_client = init_chroma_client("./.chroma_store")

    return retrieve_images(query_text_embd, chroma_client)
