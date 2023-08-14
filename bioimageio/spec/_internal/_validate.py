import collections.abc
import dataclasses
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from keyword import iskeyword
from pathlib import Path, PurePath
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Hashable,
    Mapping,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
)

import annotated_types
import packaging.version
from dateutil.parser import isoparse
from pydantic import AnyUrl, DirectoryPath, GetCoreSchemaHandler, functional_validators
from pydantic_core.core_schema import CoreSchema, no_info_after_validator_function
from typing_extensions import NotRequired, TypedDict

from bioimageio.spec._internal._constants import ERROR

if TYPE_CHECKING:
    from bioimageio.spec.shared.types import FileSource, RelativePath, WarningLevel


if sys.version_info < (3, 10):
    SLOTS: Dict[str, Any] = {}
else:
    SLOTS = {"slots": True}


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
        from bioimageio.spec.shared.types import FileSource, RelativePath

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

    raise AssertionError(f"'{dt}' not a string or datetime.")


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


def is_valid_raw_leaf_value(value: Any) -> bool:
    from bioimageio.spec.shared.types import RawLeafValue

    return isinstance(value, get_args(RawLeafValue))


def is_valid_raw_mapping(value: Union[Any, Mapping[Any, Any]]) -> bool:
    return isinstance(value, collections.abc.Mapping) and all(
        isinstance(k, str) and is_valid_raw_value(v) for k, v in value.items()
    )


def is_valid_raw_sequence(value: Union[Any, Sequence[Any]]) -> bool:
    return isinstance(value, collections.abc.Sequence) and all(is_valid_raw_value(v) for v in value)


def is_valid_raw_value(value: Any) -> bool:
    return any(is_valid(value) for is_valid in (is_valid_raw_leaf_value, is_valid_raw_mapping, is_valid_raw_sequence))


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


class ValContext(TypedDict):
    """internally used validation context"""

    root: Union[DirectoryPath, AnyUrl]
    """url/path serving as base to any relative file paths. Default provided as data field `root`.0"""

    warning_level: "WarningLevel"
    """raise warnings of severity s as validation errors if s >= `warning_level`"""

    file_name: str
    """The file name of the RDF used only for reporting"""

    original_format: NotRequired[Tuple[int, int, int]]
    """original format version of the validation data (set dynamically during validation of resource descriptions)."""

    collection_base_content: NotRequired[Dict[str, Any]]
    """Collection base content (set dynamically during validation of collection resource descriptions)."""


def get_validation_context(
    root: Union[DirectoryPath, AnyUrl] = Path(), warning_level: "WarningLevel" = ERROR, file_name: str = "rdf.yaml"
) -> ValContext:
    return ValContext(root=root, warning_level=warning_level, file_name=file_name)


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
