# autogen: start
from bioimageio.spec.shared import fields
from . import nodes, raw_nodes, schema, utils
from .raw_nodes import ModelFormatVersion

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore

fields = fields


export_package = utils.IO.export_package
get_package_content = utils.IO.get_package_content
load_node = utils.IO.load_node
load_raw_node = utils.IO.load_raw_node
save_raw_node = utils.IO.save_raw_node
serialize_raw_node_to_dict = utils.IO.serialize_raw_node_to_dict

format_version = get_args(raw_nodes.ModelFormatVersion)[-1]

# autogen: stop
