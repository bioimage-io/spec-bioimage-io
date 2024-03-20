from typing import Any, ClassVar, Type

from pydantic import GetCoreSchemaHandler, RootModel
from pydantic_core.core_schema import (
    CoreSchema,
    no_info_after_validator_function,
)


class ValidatedString(str):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[str]
    """the pydantic root model to validate the string"""
    # TODO: should we use a TypeAdapter instead?
    # TODO: with future py version:  RootModel[Any] -> RootModel[str | "literal string type"]
    _validated: Any  # pyright: ignore[reportUninitializedInstanceVariable]  # initalized in __new__

    def __new__(cls, object: object):
        self = super().__new__(cls, object)
        self._validated = cls.root_model.model_validate(str(self)).root
        return self

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return no_info_after_validator_function(cls, handler(str))
