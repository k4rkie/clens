import logging


def configure_logging(*, server: bool = False) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            if server
            else "[%(levelname)s] %(name)s: %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S" if server else None,
        force=server,
    )

    logging.getLogger("uvicorn.access").disabled = True

    for logger_name in (
        "chromadb",
        "filelock",
        "huggingface_hub",
        "httpcore",
        "httpx",
        "PIL",
        "sentence_transformers",
        "tokenizers",
        "transformers",
        "urllib3",
    ):
        logging.getLogger(logger_name).setLevel(logging.WARNING)
