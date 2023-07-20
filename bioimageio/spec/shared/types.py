from __future__ import annotations

import pathlib
from datetime import datetime
from typing import Any, Mapping, Sequence, Tuple, TypeVar, Union
from urllib.parse import urljoin

import annotated_types
from pydantic import AnyUrl, GetCoreSchemaHandler, HttpUrl, PydanticUserError, ValidationInfo, constr
from pydantic.functional_validators import AfterValidator, BeforeValidator
from pydantic_core import core_schema
from typing_extensions import Annotated, LiteralString

from bioimageio.spec._internal._constants import SI_UNIT_REGEX
from bioimageio.spec._internal._generated_spdx_license_type import DeprecatedLicenseId, LicenseId
from bioimageio.spec._internal._validate import (
    RestrictCharacters,
    validate_datetime,
    validate_identifier,
    validate_is_not_keyword,
    validate_orcid_id,
    validate_unique_entries,
    validate_version,
)

T = TypeVar("T")
L = TypeVar("L", bound=LiteralString)

NonEmpty = Annotated[T, annotated_types.MinLen(1)]


AxesStr = Annotated[str, RestrictCharacters("bitczyx"), AfterValidator(validate_unique_entries)]
AxesInCZYX = Annotated[str, RestrictCharacters("czyx"), AfterValidator(validate_unique_entries)]
CapitalStr = Annotated[NonEmpty[str], AfterValidator(str.capitalize)]
Datetime = Annotated[datetime, BeforeValidator(validate_datetime)]
"""Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."""

OrcidId = Annotated[str, AfterValidator(validate_orcid_id)]
DeprecatedLicenseId = DeprecatedLicenseId
Identifier = Annotated[
    NonEmpty[str],
    annotated_types.LowerCase,
    AfterValidator(validate_identifier),
    AfterValidator(validate_is_not_keyword),
]
LicenseId = LicenseId
RawLeafValue = Union[int, float, str, bool, None]
RawMapping = Mapping[str, "RawValue"]
RawSequence = Sequence["RawValue"]
RawValue = Union[RawLeafValue, RawSequence, RawMapping]
Sha256 = Annotated[str, annotated_types.Len(64, 64)]
SiUnit = Annotated[
    constr(min_length=1, pattern=SI_UNIT_REGEX), AfterValidator(lambda s: s.replace("×", "·").replace("*", "·"))
]
UniqueTuple = Annotated[Tuple[T], AfterValidator(validate_unique_entries)]
Version = Annotated[str, AfterValidator(validate_version)]


class RelativePath:
    """A path relative to root; root may be a (relative or absolute) path or a URL."""

    _relative: pathlib.PurePosixPath
    _root: Union[AnyUrl, pathlib.Path]

    def __init__(
        self, path: Union[str, pathlib.Path, RelativePath], /, *, root: Union[AnyUrl, pathlib.Path] = pathlib.Path()
    ) -> None:
        self._relative = path._relative if isinstance(path, RelativePath) else pathlib.PurePosixPath(path)
        self._root = root
        self._check_exists()

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
        return f"RelativePath({self._relative}, root={self._root}"

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

    @property
    def root(self):
        return self._root

    @property
    def absolute(self):
        if isinstance(self._root, pathlib.Path):
            return self._root / self._relative
        else:
            return AnyUrl(urljoin(str(self._root), str(self._relative)))

    def _check_exists(self) -> None:
        if isinstance((p := self.absolute), pathlib.Path) and not p.exists():
            raise ValueError(f"{p} does not exist")

    @classmethod
    def _validate(cls, value: Union[pathlib.Path, str], info: ValidationInfo):
        if info.context is None or "root" not in info.context:
            raise PydanticUserError("missing 'root' context for {klass}", code=None)

        root = info.context["root"]
        if not isinstance(root, (AnyUrl, pathlib.Path)):
            raise ValueError(
                "{klass} expected root context to be of type 'pathlib.Path' or 'pydantic.AnyUrl', "
                f"but got {root} of type '{type(root)}'"
            )

        return cls(value, root=root)


class RelativeFilePath(RelativePath):
    def _check_exists(self) -> None:
        if isinstance((p := self.absolute), pathlib.Path) and not p.is_file():
            raise ValueError(f"{p} does not point to an existing file")


class RelativeDirectory(RelativePath):
    def _check_exists(self) -> None:
        if isinstance((p := self.absolute), pathlib.Path) and not p.is_dir():
            raise ValueError(f"{p} does not point to an existing directory")


FileSource = Union[HttpUrl, RelativeFilePath]
Loc = Tuple[Union[int, str], ...]
