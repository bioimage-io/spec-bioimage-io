from typing import Any, Dict, Tuple, Union

from pydantic import AnyUrl, HttpUrl

from bioimageio.spec._internal._constants import IN_PACKAGE_MESSAGE
from bioimageio.spec._internal.base_nodes import FrozenDictNode, Node
from bioimageio.spec.types import Loc, RelativeFilePath


def fill_resource_package_content(
    package_content: Dict[Loc, Union[HttpUrl, RelativeFilePath]],
    node: Node,
    node_loc: Loc,
    package_urls: bool,
):
    field_value: Union[Tuple[Any, ...], Node, Any]
    for field_name, field_value in node:
        loc = node_loc + (field_name,)
        # nested node
        if isinstance(field_value, Node):
            if not isinstance(field_value, FrozenDictNode):
                fill_resource_package_content(package_content, field_value, loc, package_urls)

        # nested node in tuple
        elif isinstance(field_value, tuple):
            for i, fv in enumerate(field_value):
                if isinstance(fv, Node) and not isinstance(fv, FrozenDictNode):
                    fill_resource_package_content(package_content, fv, loc + (i,), package_urls)

        elif (node.model_fields[field_name].description or "").startswith(IN_PACKAGE_MESSAGE):
            if isinstance(field_value, RelativeFilePath):
                src = field_value
            elif isinstance(field_value, AnyUrl):
                if not package_urls:
                    continue
                src = field_value
            else:
                raise NotImplementedError(f"Package field of type {type(field_value)} not implemented.")

            package_content[loc] = src
