import json
import pathlib

from .build_spec import add_weights, build_spec, serialize_spec


with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__ = json.load(f)["version"]
