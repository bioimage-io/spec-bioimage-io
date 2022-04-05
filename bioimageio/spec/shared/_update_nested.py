from typing import TypeVar, Union

from .node_transformer import NestedUpdateTransformer
from .raw_nodes import RawNode

UpdateType = TypeVar("UpdateType")


def update_nested(data: Union[dict, list, RawNode], update: UpdateType) -> Union[dict, list, RawNode, UpdateType]:
    return NestedUpdateTransformer().transform(data, update)
