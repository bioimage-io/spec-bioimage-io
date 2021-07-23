import json
import pathlib

from . import model, rdf, shared
from .delegator import (
    ensure_raw_node,
    export_package,
    get_package_content,
    load_node,
    load_raw_node,
    save_raw_node,
    serialize_raw_node,
    serialize_raw_node_to_dict,
)

with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__ = json.load(f)["version"]
