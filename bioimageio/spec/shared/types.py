from __future__ import annotations

import pathlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Literal, Mapping, Sequence, Tuple, TypeVar, Union
from urllib.parse import urljoin

import annotated_types
from pydantic import (
    AnyUrl,
    DirectoryPath,
    GetCoreSchemaHandler,
    HttpUrl,
    ValidationInfo,
    constr,
    functional_validators,
)
from pydantic_core import core_schema
from typing_extensions import Annotated, LiteralString

from bioimageio.spec._internal._constants import SI_UNIT_REGEX
from bioimageio.spec._internal._generated_spdx_license_type import DeprecatedLicenseId, LicenseId
from bioimageio.spec._internal._validate import (
    SLOTS,
    RestrictCharacters,
    capitalize_first_letter,
    validate_datetime,
    validate_identifier,
    validate_is_not_keyword,
    validate_orcid_id,
    validate_unique_entries,
    validate_version,
)
from bioimageio.spec.shared.validation import ValidationContext, validation_context_var


@dataclass(frozen=True, **SLOTS)
class AfterValidator(functional_validators.AfterValidator):
    def __str__(self):
        return f"AfterValidator({self.func.__name__})"


@dataclass(frozen=True, **SLOTS)
class BeforeValidator(functional_validators.BeforeValidator):
    def __str__(self):
        return f"BeforeValidator({self.func.__name__})"


@dataclass(frozen=True, **SLOTS)
class Predicate(annotated_types.Predicate):
    def __str__(self):
        return f"Predicate({self.func.__name__})"


T = TypeVar("T")
S = TypeVar("S", bound=Sequence[Any])
L = TypeVar("L", bound=LiteralString)

NonEmpty = Annotated[S, annotated_types.MinLen(1)]


AxesStr = Annotated[str, RestrictCharacters("bitczyx"), AfterValidator(validate_unique_entries)]
AxesInCZYX = Annotated[str, RestrictCharacters("czyx"), AfterValidator(validate_unique_entries)]
CapitalStr = Annotated[NonEmpty[str], AfterValidator(capitalize_first_letter)]
Datetime = Annotated[datetime, BeforeValidator(validate_datetime)]
"""Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."""

OrcidId = Annotated[str, AfterValidator(validate_orcid_id)]
DeprecatedLicenseId = DeprecatedLicenseId
Identifier = Annotated[
    NonEmpty[str],
    Predicate(str.islower),
    AfterValidator(validate_identifier),
    AfterValidator(validate_is_not_keyword),
]
LicenseId = LicenseId
RawLeafValue = Union[int, float, str, bool, None]
RawMapping = Mapping[str, "RawValue"]
RawSequence = Sequence["RawValue"]
RawValue = Union[RawLeafValue, RawSequence, RawMapping]
RawDict = Dict[str, RawValue]
Sha256 = Annotated[str, annotated_types.Len(64, 64)]
SiUnit = Annotated[
    constr(min_length=1, pattern=SI_UNIT_REGEX),
    BeforeValidator(lambda s: s.replace("×", "·").replace("*", "·").replace(" ", "·") if isinstance(s, str) else s),
]
Unit = Union[Literal["px", "arbitrary intensity"], SiUnit]
UniqueTuple = Annotated[Tuple[T], AfterValidator(validate_unique_entries)]
Version = Annotated[str, AfterValidator(validate_version)]


class RelativePath:
    """A path relative to root; root may be a (relative or absolute) path or a URL."""

    _relative: pathlib.PurePosixPath
    _root: Union[AnyUrl, pathlib.Path]

    def __init__(self, path: Union[str, pathlib.Path, RelativePath]) -> None:
        super().__init__()
        self._relative = path._relative if isinstance(path, RelativePath) else pathlib.PurePosixPath(path)
        self._root = validation_context_var.get().root  # save root from current context

    @property
    def __members(self):
        return (self._relative, self._root)

    def __eq__(self, __value: object) -> bool:
        return type(__value) is type(self) and self.__members == __value.__members

    def __hash__(self) -> int:
        return hash(self.__members)

    def __str__(self) -> str:
        return str(self._relative)

    def __repr__(self) -> str:
        return f"RelativePath('{self._relative.as_posix()}')"

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls._validate,
            core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    core_schema.is_instance_schema(pathlib.Path),
                    core_schema.str_schema(),
                ]
            ),
            serialization=core_schema.to_string_ser_schema(),
        )

    @property
    def relative(self):
        return self._relative

    def get_root(self):
        # prefer current context over context at init
        return validation_context_var.get(ValidationContext(root=self._root)).root

    def get_absolute(self):
        root = self.get_root()
        if isinstance(root, pathlib.Path):
            return root / self._relative
        else:
            return AnyUrl(urljoin(str(root), str(self._relative)))

    def _check_exists(self) -> None:
        if isinstance((p := self.get_absolute()), pathlib.Path) and not p.exists():
            raise ValueError(f"{p} does not exist")

    @classmethod
    def _validate(cls, value: Union[pathlib.Path, str], info: ValidationInfo):
        ret = cls(value)
        ret._check_exists()
        return ret


class RelativeFilePath(RelativePath):
    def _check_exists(self) -> None:
        if isinstance((p := self.get_absolute()), pathlib.Path) and not p.is_file():
            raise ValueError(f"{p} does not point to an existing file")


class RelativeDirectory(RelativePath):
    def _check_exists(self) -> None:
        if isinstance((p := self.get_absolute()), pathlib.Path) and not p.is_dir():
            raise ValueError(f"{p} does not point to an existing directory")


FileSource = Union[HttpUrl, RelativeFilePath]
Loc = Tuple[Union[int, str], ...]
