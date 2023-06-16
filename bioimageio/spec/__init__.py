import json
import pathlib

with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__ = json.load(f)["version"]

from . import collection, generic, model, shared

__all__ = [
    "__version__",
    "collection",
    "generic",
    "model",
    "shared",
]
