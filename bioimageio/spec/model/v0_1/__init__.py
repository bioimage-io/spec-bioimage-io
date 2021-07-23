from bioimageio.spec.shared import fields
from . import nodes, raw_nodes, schema, utils

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore

fields = fields

load_raw_node = utils.IO.load_raw_node
load_node = utils.IO.load_node
save_raw_node = utils.IO.save_raw_node
serialize_raw_node_to_dict = utils.IO.serialize_raw_node_to_dict

format_version = get_args(raw_nodes.FormatVersion)[-1]
