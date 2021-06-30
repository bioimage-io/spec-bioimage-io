from bioimageio.spec.shared import fields, get_args as _get_args
from . import nodes, raw_nodes, schema, utils
from .converters import maybe_convert_manifest, maybe_convert_model, maybe_update_model
from .raw_nodes import ModelFormatVersion

fields = fields


get_nn_instance = utils.get_nn_instance
load_raw_model = utils.ModelLoader.load_raw_model
load_model = utils.ModelLoader.load_model
save_raw_model = utils.ModelLoader.save_raw_model
serialize_raw_model_to_dict = utils.ModelLoader.serialize_raw_model_to_dict
export_package = utils.ModelLoader.export_package

__version__ = _get_args(ModelFormatVersion)[-1]
