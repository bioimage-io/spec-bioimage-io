from bioimageio.spec.shared import fields, get_args as _get_args
from . import nodes, raw_nodes, schema, utils
from .raw_nodes import ModelFormatVersion

fields = fields

__version__ = _get_args(ModelFormatVersion)[-1]

load_raw_node = utils.IO.load_raw_node
load_node = utils.IO.load_node
save_raw_node = utils.IO.save_raw_node
serialize_raw_node_to_dict = utils.IO.serialize_raw_node_to_dict
