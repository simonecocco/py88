import os


def check_file(file: str) -> bool:
    return os.path.exists(file) and os.path.isfile(file) and os.access(file, os.R_OK)
