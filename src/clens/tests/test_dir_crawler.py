from pathlib import Path
import pytest
from clens.dir_crawler import find_images


def test_find_images(tmp_path: Path):
    (tmp_path / "img1.jpg").touch()
    (tmp_path / "img1.png").touch()
    (tmp_path / "test.md").touch()
    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    (sub_dir / "img2.png").touch()
    (sub_dir / "img2.jpg").touch()

    result = find_images(tmp_path)

    assert {r.name for r in result} == {"img1.jpg", "img1.png", "img2.png", "img2.jpg"}


def test_find_images_empty_dir(tmp_path: Path):
    result = find_images(tmp_path)
    assert result == []


def test_find_images_missing_dir(tmp_path: Path):
    missing_dir = tmp_path / "non_existent_dir"
    with pytest.raises(FileNotFoundError, match="No such directory found"):
        find_images(missing_dir)


def test_find_images_file_path(tmp_path: Path):
    file_path = tmp_path / "img.png"
    file_path.touch()
    with pytest.raises(
        NotADirectoryError, match="Path must be a directory and not a file"
    ):
        find_images(file_path)
