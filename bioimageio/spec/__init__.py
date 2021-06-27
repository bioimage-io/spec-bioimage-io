from . import v0_1, v0_3
from .build_spec import build_spec

# autogen: start
from bioimageio.spec.shared import fields, get_args as _get_args
from . import nodes, raw_nodes, schema, utils
from .converters import maybe_convert_manifest, maybe_convert_model
from .raw_nodes import ModelFormatVersion

fields = fields


get_nn_instance = utils.get_nn_instance
load_raw_model = utils.ModelLoader.load_raw_model
load_model = utils.ModelLoader.load_model
save_raw_model = utils.ModelLoader.save_raw_model
serialize_raw_model = utils.ModelLoader.serialize_raw_model

__version__ = _get_args(ModelFormatVersion)[-1]

# autogen: stop
