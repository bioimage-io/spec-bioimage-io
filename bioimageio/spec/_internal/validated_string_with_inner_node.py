from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Type, TypeVar

from pydantic import SerializationInfo, SerializerFunctionWrapHandler, model_serializer

from .node import Node
from .validated_string import ValidatedString

InnerNodeT = TypeVar("InnerNodeT", bound=Node)


class ValidatedStringWithInnerNode(ABC, ValidatedString, Generic[InnerNodeT]):
    """A validated string with further validation and serialization using a `Node`"""

    _inner_node_class: Type[InnerNodeT]
    _inner_node: InnerNodeT  # initalized in _after_validator called in __new__

    @model_serializer(mode="wrap")
    def _serialize(
        self, handler: SerializerFunctionWrapHandler, info: SerializationInfo
    ):
        _ = self._inner_node.model_dump(mode=info.mode)
        return handler(
            self,
            info,  # pyright: ignore[reportArgumentType]  # taken from pydantic docs
        )

    @classmethod
    @abstractmethod
    def _get_data(cls, valid_string_data: str) -> Dict[str, Any]: ...

    def _after_validator(self):
        data = self._get_data(self._validated)
        self._inner_node = self._inner_node_class.model_validate(data)
        return super()._after_validator()
