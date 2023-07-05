import collections.abc
import dataclasses
import re
import sys
from datetime import datetime
from keyword import iskeyword
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Hashable,
    Mapping,
    Sequence,
    Type,
    Union,
    get_args,
)

import packaging.version
from pydantic import AnyUrl, GetCoreSchemaHandler
from pydantic_core.core_schema import CoreSchema, no_info_after_validator_function

if TYPE_CHECKING:
    from .types import FileSource


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


def validate_datetime(dt: Union[datetime, str, Any]) -> Union[datetime, str]:
    if isinstance(dt, datetime):
        return dt
    elif isinstance(dt, str):
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))

    raise AssertionError(f"'{dt}' not a string or datetime.")


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


def is_valid_raw_value(value: Any) -> bool:
    return any(is_valid(value) for is_valid in (is_valid_raw_leaf_value, is_valid_raw_mapping, is_valid_raw_sequence))


def is_valid_raw_leaf_value(value: Any) -> bool:
    from bioimageio.spec.shared.types import RawLeafValue

    return isinstance(value, get_args(RawLeafValue))


def is_valid_raw_mapping(value: Union[Any, Mapping[Any, Any]]) -> bool:
    return isinstance(value, collections.abc.Mapping) and all(
        isinstance(k, str) and is_valid_raw_value(v) for k, v in value.items()
    )


def is_valid_raw_sequence(value: Union[Any, Sequence[Any]]) -> bool:
    return isinstance(value, collections.abc.Sequence) and all(is_valid_raw_value(v) for v in value)


def validate_datetime_iso8601(value: Union[datetime, str, Any]) -> datetime:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass

    raise ValueError(
        f"Invalid isoformat string '{value}'. Please follow ISO 8601 with restrictions listed "
        "[here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."
    )


def validate_suffix(value: "FileSource", *suffixes: str) -> "FileSource":
    assert all(suff.startswith(".") for suff in suffixes)
    if isinstance(value, AnyUrl):
        if value.path is None or "." not in value.path:
            suffix = None
        else:
            suffix = "." + value.path.split(".")[-1]
    else:
        suffix = value.relative.suffixes[-1]

    if suffix not in suffixes:
        raise ValueError(f"{suffix} not in {suffixes}")

    return value


def validate_orcid_id(orcid_id: str):
    if len(orcid_id) == 19 and all(orcid_id[idx] == "-" for idx in [4, 9, 14]):
        check = 0
        for n in orcid_id[:4] + orcid_id[5:9] + orcid_id[10:14] + orcid_id[15:]:
            # adapted from stdnum.iso7064.mod_11_2.checksum()
            check = (2 * check + int(10 if n == "X" else n)) % 11
        if check == 1:
            return orcid_id  # valid

    raise ValueError(f"'{orcid_id} is not a valid ORCID iD in hyphenated groups of 4 digits.")
