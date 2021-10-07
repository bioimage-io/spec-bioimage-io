import json
import pathlib

from . import model, rdf, shared
from .commands import validate
from .io_ import get_resource_package_content, load_raw_resource_description, serialize_raw_resource_description_to_dict

with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__ = json.load(f)["version"]
