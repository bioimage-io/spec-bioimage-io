from . import v0_1, v0_3
from .build_spec import build_spec

# autogen: start
from bioimageio.spec.shared import fields
from . import nodes, raw_nodes, schema, utils
from .converters import maybe_convert_manifest, maybe_convert_model
from .raw_nodes import ModelFormatVersion

fields = fields


get_nn_instance = utils.get_nn_instance
download_uri_to_local_path = utils.download_uri_to_local_path
load_raw_model = utils.load_raw_model
load_model = utils.load_model

# autogen: stop

# assuming schema will always be part of spec
from bioimageio.spec.shared.common import get_args
from .raw_nodes import ModelFormatVersion

__version__ = get_args(ModelFormatVersion)[-1]
