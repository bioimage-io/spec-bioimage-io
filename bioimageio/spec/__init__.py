import json
import pathlib

from . import model, rdf, shared
from .delegator import (
    ensure_raw_resource_description,
    export_resource_package,
    get_resource_package_content,
    load_raw_resource_description,
    load_resource_description,
    save_raw_resource_description,
    serialize_raw_resource_description,
    serialize_raw_resource_description_to_dict,
)

with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__ = json.load(f)["version"]
