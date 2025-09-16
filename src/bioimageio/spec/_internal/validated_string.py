from typing import Any, ClassVar, Type

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, RootModel
from pydantic.json_schema import JsonSchemaValue
from pydantic_core.core_schema import (
    CoreSchema,
    no_info_after_validator_function,
)
from typing_extensions import Self


class ValidatedString(str):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[str]
    """the pydantic root model to validate the string"""
    # TODO: should we use a TypeAdapter instead?
    # TODO: with future py version:  RootModel[Any] -> RootModel[str | "literal string type"]
    _validated: Any  # initalized in __new__

    def __new__(cls, object: object):
        _validated = cls.root_model.model_validate(object).root
        self = super().__new__(cls, _validated)
        self._validated = _validated
        return self._after_validator()

    def _after_validator(self) -> Self:
        """add validation after the `root_model`"""
        return self

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return no_info_after_validator_function(cls, handler(str))

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = cls.root_model.model_json_schema(mode=handler.mode)
        json_schema["title"] = cls.__name__.strip("_")
        if cls.__doc__:
            json_schema["description"] = cls.__doc__

        return json_schema
