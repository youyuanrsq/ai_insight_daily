from datetime import datetime
import os
from pathlib import Path


def get_file_path(file_name: str) -> Path:
    """return the file path of a file name

    Args:
        file_name (str): the name of the file

    Returns:
        Path: the file path
    """
    n_date = datetime.today().date().strftime("%Y-%m-%d")
    dir_name = Path(f"./data/{n_date}")
    dir_name.mkdir(parents=True, exist_ok=True)
    f_path = dir_name / f"{file_name}.txt"

    return f_path


def strip_string(string: str) -> str:
    """strip a title string

    Args:
        string (str): string to be stripped

    Returns:
        str: stripped string
    """
    return string.strip().replace("\n", "").replace("\t", "").replace(" ", "-")
