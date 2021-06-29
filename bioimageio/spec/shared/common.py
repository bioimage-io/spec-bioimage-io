import os
import pathlib
import tempfile
from typing import Generic

from ruamel.yaml import YAML

try:
    from typing import Literal, get_args, get_origin, Protocol
except ImportError:
    from typing_extensions import Literal, get_args, get_origin, Protocol  # type: ignore


def get_args_flat(tp):
    flat_args = []
    for a in get_args(tp):
        orig = get_origin(a)
        if orig is Literal or orig is Generic:
            flat_args += list(get_args(a))
        else:
            flat_args.append(a)

    return tuple(flat_args)


yaml = YAML(typ="safe")

BIOIMAGEIO_CACHE_PATH = pathlib.Path(
    os.getenv("BIOIMAGEIO_CACHE_PATH", pathlib.Path(tempfile.gettempdir()) / "bioimageio_cache")
)


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
