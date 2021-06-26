from bioimageio.spec.shared import fields, get_args as _get_args
from . import nodes, raw_nodes, schema
from .raw_nodes import ModelFormatVersion

fields = fields


def maybe_convert_model(data):
    return data


def maybe_convert_manifest(data):
    return data


__version__ = _get_args(ModelFormatVersion)[-1]
