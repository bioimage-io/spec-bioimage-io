from bioimageio.spec.shared import fields
from . import nodes, raw_nodes, schema, utils
from .raw_nodes import FormatVersion

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore

fields = fields

load_raw_node = utils.IO.load_raw_resource_description
load_node = utils.IO.load_resource_description
save_raw_node = utils.IO.save_raw_resource_description
serialize_raw_node_to_dict = utils.IO.serialize_raw_resource_description_to_dict

format_version = get_args(FormatVersion)[-1]
