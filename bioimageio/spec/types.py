from __future__ import annotations

import pathlib
from datetime import datetime
from typing import Any, Dict, Literal, Mapping, Sequence, Tuple, TypeVar, Union
from urllib.parse import urljoin

import annotated_types
from pydantic import AnyUrl, DirectoryPath, FilePath, GetCoreSchemaHandler, HttpUrl, StringConstraints, ValidationInfo
from pydantic_core import core_schema
from typing_extensions import Annotated, LiteralString, NotRequired, TypedDict

from bioimageio.spec._internal.constants import SI_UNIT_REGEX
from bioimageio.spec._internal.field_validation import (
    AfterValidator,
    BeforeValidator,
    Predicate,
    RestrictCharacters,
    capitalize_first_letter,
    validate_datetime,
    validate_identifier,
    validate_is_not_keyword,
    validate_orcid_id,
    validate_unique_entries,
    validate_version,
)
from bioimageio.spec._internal.generated_spdx_license_type import DeprecatedLicenseId, LicenseId

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
RawMapping = Mapping[RawLeafValue, "RawValue"]
RawStringMapping = Mapping[str, "RawValue"]
RawSequence = Sequence["RawValue"]
RawValue = Union[RawLeafValue, RawSequence, RawMapping]
RawStringDict = Dict[str, RawValue]
Sha256 = Annotated[str, annotated_types.Len(64, 64)]
SiUnit = Annotated[
    str,
    StringConstraints(min_length=1, pattern=SI_UNIT_REGEX),
    BeforeValidator(lambda s: s.replace("×", "·").replace("*", "·").replace(" ", "·") if isinstance(s, str) else s),
]
Unit = Union[Literal["px", "arbitrary intensity"], SiUnit]
UniqueTuple = Annotated[Tuple[T], AfterValidator(validate_unique_entries)]
Version = Annotated[str, AfterValidator(validate_version)]

Severity = Literal[20, 30, 35]
"""Severity of a warning"""

WarningLevel = Literal[Severity, 50]
"""With warning level x raise warnings of severity >=x"""

SeverityName = Literal["info", "warning", "alert"]


class RelativePath:
    path: pathlib.PurePosixPath

    def __init__(self, path: Union[str, pathlib.Path, RelativePath]) -> None:
        super().__init__()
        self.path = path.path if isinstance(path, RelativePath) else pathlib.PurePosixPath(path)

    @property
    def __members(self):
        return (self.path,)

    def __eq__(self, __value: object) -> bool:
        return type(__value) is type(self) and self.__members == __value.__members

    def __hash__(self) -> int:
        return hash(self.__members)

    def __str__(self) -> str:
        return self.path.as_posix()

    def __repr__(self) -> str:
        return f"RelativePath('{self.path.as_posix()}')"

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

    def get_absolute(self, root: Union[DirectoryPath, AnyUrl]) -> Union[FilePath, AnyUrl]:
        if isinstance(root, pathlib.Path):
            return root / self.path
        else:
            return AnyUrl(urljoin(str(root), str(self.path)))

    def _check_exists(self, root: Union[DirectoryPath, AnyUrl]) -> None:
        if isinstance((p := self.get_absolute(root)), pathlib.Path) and not p.exists():
            raise ValueError(f"{p} does not exist")

    @classmethod
    def _validate(cls, value: Union[pathlib.Path, str], info: ValidationInfo):
        if isinstance(value, str) and (value.startswith("https://") or value.startswith("http://")):
            raise ValueError(f"{value} looks like a URL, not a relative path")

        ret = cls(value)
        root = (info.context or {}).get("root")
        if root is not None:
            ret._check_exists(root)

        return ret


class RelativeFilePath(RelativePath):
    def _check_exists(self, root: Union[DirectoryPath, AnyUrl]) -> None:
        if isinstance((p := self.get_absolute(root)), pathlib.Path) and not p.is_file():
            raise ValueError(f"{p} does not point to an existing file")


class RelativeDirectory(RelativePath):
    def _check_exists(self, root: Union[DirectoryPath, AnyUrl]) -> None:
        if isinstance((p := self.get_absolute(root)), pathlib.Path) and not p.is_dir():
            raise ValueError(f"{p} does not point to an existing directory")


FileSource = Union[HttpUrl, RelativeFilePath]
FileName = str
Loc = Tuple[Union[int, str], ...]


class ValidationContext(TypedDict):
    root: NotRequired[Union[DirectoryPath, AnyUrl]]
    """url/path serving as base to any relative file paths. Default provided as data field `root`.0"""

    file_name: NotRequired[str]
    """The file name of the RDF used only for reporting"""

    warning_level: NotRequired[WarningLevel]
    """raise warnings of severity s as validation errors if s >= `warning_level`"""
