from pathlib import Path

image_types = ["jpg", "png"]


def find_images(root_dir: str | Path) -> list[Path]:
    root = Path(root_dir)
    if root.is_file():
        raise NotADirectoryError(f"Path must be a directory and not a file: {root}")
    if not root.exists():
        raise FileNotFoundError(f"No such directory found: {root}")

    file_paths: list[Path] = []
    for image_type in image_types:
        for file_path in root.rglob(f"*.{image_type}"):
            file_paths.append(file_path.absolute())

    return file_paths
