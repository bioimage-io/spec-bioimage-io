import json
import pathlib

from . import model, rdf, shared

with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__ = json.load(f)["version"]

from .io_ import load_raw_resource_description, serialize_raw_resource_description_to_dict, get_resource_package_content
