import json
import pathlib

from . import v0_1, v0_3
from .build_spec import add_weights, build_spec, serialize_spec

# autogen: start
from bioimageio.spec.shared import fields
from . import nodes, raw_nodes, schema, utils
from .raw_nodes import ModelFormatVersion

fields = fields


export_package = utils.IO.export_package
get_package_content = utils.IO.get_package_content
load_node = utils.IO.load_node
load_raw_node = utils.IO.load_raw_node
save_raw_node = utils.IO.save_raw_node
serialize_raw_node_to_dict = utils.IO.serialize_raw_node_to_dict

# autogen: stop

with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__ = json.load(f)["version"]
