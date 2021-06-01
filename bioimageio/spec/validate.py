import pathlib

from marshmallow.validate import *  # noqa


def is_relative_path(path_str: str):
    return not pathlib.Path(path_str).is_absolute()
