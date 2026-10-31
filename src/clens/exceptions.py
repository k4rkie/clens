class ClensError(Exception):
    error_type: str = "ClensError"


class NoImagesFoundError(ClensError):
    error_type: str = "NoImagesFound"


class InvalidImageError(ClensError):
    error_type: str = "InvalidImageError"
