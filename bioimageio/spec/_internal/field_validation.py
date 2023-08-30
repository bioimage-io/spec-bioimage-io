from __future__ import annotations

import collections.abc
import dataclasses
import pathlib
import re
from dataclasses import dataclass
from datetime import datetime
from keyword import iskeyword
from pathlib import Path, PurePath, PurePosixPath
from typing import TYPE_CHECKING, Any, Dict, Hashable, Mapping, Sequence, Tuple, Type, TypeVar, Union, get_args
from urllib.parse import urljoin

import annotated_types
import packaging.version
from dateutil.parser import isoparse
from pydantic import AnyUrl, DirectoryPath, FilePath, GetCoreSchemaHandler, ValidationInfo, functional_validators
from pydantic_core import core_schema
from pydantic_core.core_schema import CoreSchema, no_info_after_validator_function
from typing_extensions import NotRequired, TypedDict

from bioimageio.spec._internal.constants import ERROR, SLOTS

if TYPE_CHECKING:
    from bioimageio.spec.types import FileSource, WarningLevel


class RelativePath:
    path: PurePosixPath

    def __init__(self, path: Union[str, Path, RelativePath]) -> None:
        super().__init__()
        self.path = (
            path.path
            if isinstance(path, RelativePath)
            else PurePosixPath(path.as_posix())
            if isinstance(path, Path)
            else PurePosixPath(Path(path).as_posix())
        )

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


@dataclasses.dataclass(frozen=True, **SLOTS)
class RestrictCharacters:
    alphabet: str

    def __get_pydantic_core_schema__(self, source: Type[Any], handler: GetCoreSchemaHandler) -> CoreSchema:
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


@dataclasses.dataclass(frozen=True, **SLOTS)
class WithSuffix:
    suffix: Union[str, Sequence[str]]
    case_sensitive: bool

    def __get_pydantic_core_schema__(self, source: Type[Any], handler: GetCoreSchemaHandler) -> CoreSchema:
        from bioimageio.spec.types import FileSource

        if not self.suffix:
            raise ValueError("suffix may not be empty")

        schema = handler(source)
        if schema["type"] != str and source != FileSource and not issubclass(source, (RelativePath, PurePath)):
            raise TypeError("WithSuffix can only be applied to strings, URLs and paths")

        return no_info_after_validator_function(
            self.validate,
            schema,
        )

    def validate(self, value: "FileSource") -> "FileSource":
        if isinstance(self.suffix, str):
            return validate_suffix(value, self.suffix, case_sensitive=self.case_sensitive)
        else:
            return validate_suffix(value, *self.suffix, case_sensitive=self.case_sensitive)


def capitalize_first_letter(v: str) -> str:
    return v[:1].capitalize() + v[1:]


def validate_datetime(dt: Union[datetime, str, Any]) -> datetime:
    if isinstance(dt, datetime):
        return dt
    elif isinstance(dt, str):
        return isoparse(dt)

    raise ValueError(f"'{dt}' not a string or datetime.")


def validate_identifier(s: str) -> str:
    if not s.isidentifier():
        raise ValueError(
            f"'{s}' is not a valid (Python) identifier, "
            "see https://docs.python.org/3/reference/lexical_analysis.html#identifiers for details."
        )

    return s


def validate_is_not_keyword(s: str) -> str:
    if iskeyword(s):
        raise ValueError(f"'{s}' is a Python keyword and not allowed here.")

    return s


def validate_orcid_id(orcid_id: str):
    if len(orcid_id) == 19 and all(orcid_id[idx] == "-" for idx in [4, 9, 14]):
        check = 0
        for n in orcid_id[:4] + orcid_id[5:9] + orcid_id[10:14] + orcid_id[15:]:
            # adapted from stdnum.iso7064.mod_11_2.checksum()
            check = (2 * check + int(10 if n == "X" else n)) % 11
        if check == 1:
            return orcid_id  # valid

    raise ValueError(f"'{orcid_id} is not a valid ORCID iD in hyphenated groups of 4 digits.")


def is_valid_yaml_leaf_value(value: Any) -> bool:
    from bioimageio.spec.types import YamlLeafValue

    return isinstance(value, get_args(YamlLeafValue))


def is_valid_yaml_key(value: Union[Any, Sequence[Any]]) -> bool:
    return (
        is_valid_yaml_leaf_value(value) or isinstance(value, tuple) and all(is_valid_yaml_leaf_value(v) for v in value)
    )


def is_valid_yaml_mapping(value: Union[Any, Mapping[Any, Any]]) -> bool:
    return isinstance(value, collections.abc.Mapping) and all(
        is_valid_yaml_key(k) and is_valid_yaml_value(v) for k, v in value.items()
    )


def is_valid_yaml_sequence(value: Union[Any, Sequence[Any]]) -> bool:
    return isinstance(value, collections.abc.Sequence) and all(is_valid_yaml_value(v) for v in value)


def is_valid_yaml_value(value: Any) -> bool:
    return any(is_valid(value) for is_valid in (is_valid_yaml_key, is_valid_yaml_mapping, is_valid_yaml_sequence))


V_suffix = TypeVar("V_suffix", bound=Union[AnyUrl, PurePath, "RelativePath"])


def validate_suffix(value: V_suffix, *suffixes: str, case_sensitive: bool) -> V_suffix:
    """check final suffix"""
    assert len(suffixes) > 0, "no suffix given"
    assert all(suff.startswith(".") for suff in suffixes), "expected suffixes to start with '.'"
    if isinstance(value, AnyUrl):
        if value.path is None or "." not in value.path:
            suffix = ""
        else:
            suffix = "." + value.path.split(".")[-1]
    elif isinstance(value, PurePath):
        suffix = value.suffixes[-1]
    else:
        suffix = value.path.suffixes[-1]

    if (
        case_sensitive
        and suffix not in suffixes
        or not case_sensitive
        and suffix.lower() not in [s.lower() for s in suffixes]
    ):
        if len(suffixes) == 1:
            raise ValueError(f"Expected suffix {suffixes[0]}, but got {suffix}")
        else:
            raise ValueError(f"Expected a suffix from {suffixes}, but got {suffix}")

    return value


def validate_unique_entries(seq: Sequence[Hashable]):
    if len(seq) != len(set(seq)):
        raise ValueError("Entries are not unique.")
    return seq


def validate_version(v: str) -> str:
    if not re.fullmatch(r"^\s*" + packaging.version.VERSION_PATTERN + r"\s*$", v, re.VERBOSE | re.IGNORECASE):
        raise ValueError(
            f"'{v}' is not a valid version string, " "see https://packaging.pypa.io/en/stable/version.html for help"
        )
    return v


class ValidationContext(TypedDict):
    root: NotRequired[Union[DirectoryPath, AnyUrl]]
    """url/path serving as base to any relative file paths. Default provided as data field `root`.0"""

    file_name: NotRequired[str]
    """The file name of the RDF used only for reporting"""

    warning_level: NotRequired[WarningLevel]
    """raise warnings of severity s as validation errors if s >= `warning_level`"""


class ValContext(TypedDict):
    """internally used validation context"""

    root: Union[DirectoryPath, AnyUrl]
    """url/path serving as base to any relative file paths. Default provided as data field `root`.0"""

    warning_level: WarningLevel
    """raise warnings of severity s as validation errors if s >= `warning_level`"""

    file_name: str
    """The file name of the RDF used only for reporting"""

    original_format: NotRequired[Tuple[int, int, int]]
    """original format version of the validation data (set dynamically during validation of resource descriptions)."""

    collection_base_content: NotRequired[Dict[str, Any]]
    """Collection base content (set dynamically during validation of collection resource descriptions)."""


def get_validation_context(
    *,
    root: Union[DirectoryPath, AnyUrl] = Path(),
    warning_level: WarningLevel = ERROR,
    file_name: str = "rdf.yaml",
    **kwargs: Any,
) -> ValContext:
    return ValContext(root=root, warning_level=warning_level, file_name=file_name, **kwargs)


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
