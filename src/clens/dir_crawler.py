from pathlib import Path

image_types = ["jpg", "png"]


def find_files(root_dir: str) -> list[Path]:
    root = Path(root_dir)
    if not root.exists():
        raise NotADirectoryError("No such directory found.")

    file_paths: list[Path] = []
    for image_type in image_types:
        for file_path in root.rglob(f"*.{image_type}"):
            file_paths.append(file_path.absolute())

    return file_paths
