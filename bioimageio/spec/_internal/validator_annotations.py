import sys
from dataclasses import dataclass
from typing import Any, Dict, Type

import annotated_types
from pydantic import GetCoreSchemaHandler, functional_validators
from pydantic_core import CoreSchema
from pydantic_core.core_schema import no_info_after_validator_function

if sys.version_info < (3, 10):
    SLOTS: Dict[str, bool] = {}
    KW_ONLY: Dict[str, bool] = {}
else:
    SLOTS = {"slots": True}
    KW_ONLY = {"kw_only": True}


# TODO: make sure we use this one everywhere and not the vanilla pydantic one
@dataclass(frozen=True, **SLOTS)
class AfterValidator(functional_validators.AfterValidator):
    def __str__(self):
        return f"AfterValidator({self.func.__name__})"


# TODO: make sure we use this one everywhere and not the vanilla pydantic one
@dataclass(frozen=True, **SLOTS)
class BeforeValidator(functional_validators.BeforeValidator):
    def __str__(self):
        return f"BeforeValidator({self.func.__name__})"


# TODO: make sure we use this one everywhere and not the vanilla pydantic one
@dataclass(frozen=True, **SLOTS)
class Predicate(annotated_types.Predicate):
    def __str__(self):
        return f"Predicate({self.func.__name__})"


@dataclass(frozen=True, **SLOTS)
class RestrictCharacters:
    alphabet: str

    def __get_pydantic_core_schema__(
        self, source: Type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        if not self.alphabet:
            raise ValueError("Alphabet may not be empty")

        schema = handler(source)  # get the CoreSchema from the type / inner constraints
        if schema["type"] != "str" and not (
            schema["type"] == "function-after" and schema["schema"]["type"] == "str"
        ):
            raise TypeError("RestrictCharacters can only be applied to strings")

        return no_info_after_validator_function(
            self.validate,
            schema,
        )

    def validate(self, value: str) -> str:
        if any(c not in self.alphabet for c in value):
            raise ValueError(f"{value!r} is not restricted to {self.alphabet!r}")
        return value
