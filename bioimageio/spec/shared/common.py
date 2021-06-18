import os
import pathlib

from ruamel.yaml import YAML

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # noqa


yaml = YAML(typ="safe")

BIOIMAGEIO_CACHE_PATH = pathlib.Path(os.getenv("BIOIMAGEIO_CACHE_PATH", pathlib.Path.home() / "bioimageio_cache"))


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
