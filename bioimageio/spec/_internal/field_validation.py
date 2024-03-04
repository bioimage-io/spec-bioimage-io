from __future__ import annotations

import collections.abc
import dataclasses
import sys
from dataclasses import dataclass
from datetime import date, datetime
from typing import (
    Any,
    Dict,
    Hashable,
    Mapping,
    Sequence,
    Type,
    Union,
)

import annotated_types
from pydantic import GetCoreSchemaHandler, functional_validators
from pydantic_core.core_schema import CoreSchema, no_info_after_validator_function

if sys.version_info < (3, 10):
    SLOTS: Dict[str, bool] = {}
    KW_ONLY: Dict[str, bool] = {}
else:
    SLOTS = {"slots": True}
    KW_ONLY = {"kw_only": True}


@dataclasses.dataclass(frozen=True, **SLOTS)
class RestrictCharacters:
    alphabet: str

    def __get_pydantic_core_schema__(
        self, source: Type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        if not self.alphabet:
            raise ValueError("Alphabet may not be empty")
        schema = handler(source)  # get the CoreSchema from the type / inner constraints
        if schema["type"] != "str":
            raise TypeError("RestrictCharacters can only be applied to strings")
        return no_info_after_validator_function(
            self.validate,
            schema,
        )

    def validate(self, value: str) -> str:
        if any(c not in self.alphabet for c in value):
            raise ValueError(f"{value!r} is not restricted to {self.alphabet!r}")
        return value


def is_valid_yaml_leaf_value(value: Any) -> bool:
    return value is None or isinstance(value, (bool, date, datetime, int, float, str))


def is_valid_yaml_key(value: Union[Any, Sequence[Any]]) -> bool:
    return (
        is_valid_yaml_leaf_value(value)
        or isinstance(value, tuple)
        and all(is_valid_yaml_leaf_value(v) for v in value)
    )


def is_valid_yaml_mapping(value: Union[Any, Mapping[Any, Any]]) -> bool:
    return isinstance(value, collections.abc.Mapping) and all(
        is_valid_yaml_key(k) and is_valid_yaml_value(v) for k, v in value.items()
    )


def is_valid_yaml_sequence(value: Union[Any, Sequence[Any]]) -> bool:
    return isinstance(value, collections.abc.Sequence) and all(
        is_valid_yaml_value(v) for v in value
    )


def is_valid_yaml_value(value: Any) -> bool:
    return any(
        is_valid(value)
        for is_valid in (
            is_valid_yaml_key,
            is_valid_yaml_mapping,
            is_valid_yaml_sequence,
        )
    )


def validate_unique_entries(seq: Sequence[Hashable]):
    if len(seq) != len(set(seq)):
        raise ValueError("Entries are not unique.")
    return seq


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
