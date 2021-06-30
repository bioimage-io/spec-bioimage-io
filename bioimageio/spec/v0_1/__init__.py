from bioimageio.spec.shared import fields, get_args as _get_args
from . import nodes, raw_nodes, schema, utils
from .raw_nodes import ModelFormatVersion

fields = fields

__version__ = _get_args(ModelFormatVersion)[-1]

load_raw_model = utils.IO.load_raw_model
load_model = utils.IO.load_model
save_raw_model = utils.IO.save_raw_model
serialize_raw_model_to_dict = utils.IO.serialize_raw_model_to_dict
