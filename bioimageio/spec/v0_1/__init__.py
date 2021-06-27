from bioimageio.spec.shared import fields, get_args as _get_args
from . import nodes, raw_nodes, schema, utils
from .raw_nodes import ModelFormatVersion

fields = fields

__version__ = _get_args(ModelFormatVersion)[-1]
