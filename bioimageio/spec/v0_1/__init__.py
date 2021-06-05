from bioimageio.spec.common_utils import CommonVersionSpecificUtils
from bioimageio.spec.v0_3 import fields  # noqa; not a mistake, v0_1 does not have its own fields
from . import nodes, raw_nodes, schema
from .raw_nodes import FormatVersion

utils = CommonVersionSpecificUtils(FormatVersion.__args__[-1])


def maybe_convert_model(data):
    return data
