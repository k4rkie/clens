from pathlib import PosixPath
import pytest
from clens.dir_crawler import find_files


def test_find_files():
    assert find_files("/home/k4rkie/Documents") == [
        PosixPath("/home/k4rkie/Documents/image_1.jpg"),
        PosixPath("/home/k4rkie/Documents/image_2.png"),
    ]
    assert find_files("/home/k4rkie/Templates") == []
    with pytest.raises(NotADirectoryError, match="No such directory found"):
        find_files("/no_a_dir")
