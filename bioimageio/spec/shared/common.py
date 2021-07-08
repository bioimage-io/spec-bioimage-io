import os
import pathlib
import tempfile
from collections import UserDict
from typing import Generic, Optional

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


class NoOverridesDict(UserDict):
    def __init__(self, *args, key_exists_error_msg: Optional[str] = None, allow_if_same_value: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_exists_error_message = (
            "key {key} already exists!" if key_exists_error_msg is None else key_exists_error_msg
        )
        self.allow_if_same_value = allow_if_same_value

    def __setitem__(self, key, value):
        if key in self and (not self.allow_if_same_value or value != self[key]):
            raise ValueError(self.key_exists_error_message.format(key=key, value=value))

        super().__setitem__(key, value)
