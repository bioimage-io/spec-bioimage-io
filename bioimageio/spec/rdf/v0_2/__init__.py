from bioimageio.spec.shared import fields
from . import nodes, raw_nodes, schema, utils
from .base_nodes import FormatVersion

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore

fields = fields

export_package = utils.IO.export_resource_package
get_package_content = utils.IO.get_resource_package_content
load_node = utils.IO.load_resource_description
load_raw_node = utils.IO.load_raw_resource_description
save_raw_node = utils.IO.save_raw_resource_description
serialize_raw_node_to_dict = utils.IO.serialize_raw_resource_description_to_dict

format_version = get_args(FormatVersion)[-1]
