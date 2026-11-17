from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import (
    GetCoreSchemaHandler,
    SerializationInfo,
    SerializerFunctionWrapHandler,
)
from pydantic_core import core_schema
from pydantic_core.core_schema import CoreSchema

from .node import Node
from .validated_string import ValidatedString

InnerNodeT = TypeVar("InnerNodeT", bound=Node)


class ValidatedStringWithInnerNode(ABC, ValidatedString, Generic[InnerNodeT]):
    """A validated string with further validation and serialization using a `Node`"""

    _inner_node_class: type[InnerNodeT]
    _inner_node: InnerNodeT  # initalized in _after_validator called in __new__

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            handler(str),
            serialization=core_schema.wrap_serializer_function_ser_schema(
                cls._serialize, info_arg=True
            ),
        )

    def _serialize(
        self, handler: SerializerFunctionWrapHandler, info: SerializationInfo
    ):
        _ = self._inner_node.model_dump(mode=info.mode)
        return handler(self)

    @classmethod
    @abstractmethod
    def _get_data(cls, valid_string_data: str) -> dict[str, Any]: ...

    def _after_validator(self):
        data = self._get_data(self._validated)
        self._inner_node = self._inner_node_class.model_validate(data)
        return super()._after_validator()
