from __future__ import annotations

from datetime import datetime, timezone
from keyword import iskeyword
from typing import Any, ClassVar, Sequence, Type, TypeVar, Union

import annotated_types
from dateutil.parser import isoparse
from pydantic import PlainSerializer, RootModel, StringConstraints
from typing_extensions import Annotated, Literal

from .constants import DOI_REGEX, SI_UNIT_REGEX
from .field_warning import AfterWarner
from .io import FileSource, PermissiveFileSource, RelativeFilePath
from .io_basics import AbsoluteDirectory, AbsoluteFilePath, FileName, FilePath, Sha256
from .io_packaging import FileSource_
from .license_id import DeprecatedLicenseId, LicenseId
from .type_guards import is_sequence
from .url import HttpUrl
from .validated_string import ValidatedString
from .validator_annotations import AfterValidator, BeforeValidator
from .version_type import Version
from .warning_levels import ALERT

UTC = timezone.utc

__all__ = [
    "AbsoluteDirectory",
    "AbsoluteFilePath",
    "Datetime",
    "DeprecatedLicenseId",
    "Doi",
    "FileName",
    "FilePath",
    "FileSource",
    "FileSource_",
    "ImportantFileSource",
    "HttpUrl",
    "Identifier",
    "LicenseId",
    "LowerCaseIdentifier",
    "NotEmpty",
    "OrcidId",
    "PermissiveFileSource",
    "RelativeFilePath",
    "Sha256",
    "SiUnit",
    "Version",
]
S = TypeVar("S", bound=Sequence[Any])
A = TypeVar("A", bound=Any)
NotEmpty = Annotated[S, annotated_types.MinLen(1)]


def _validate_fair(value: Any) -> Any:
    """Raise trivial values."""
    if value is None or (is_sequence(value) and not value):
        raise ValueError("Needs to be filled for FAIR compliance")

    return value


FAIR = Annotated[
    A,
    AfterWarner(_validate_fair, severity=ALERT),
]

ImportantFileSource = FileSource_
"""DEPRECATED alias, use `FileSource` instead"""


def _validate_identifier(s: str) -> str:
    if not s.isidentifier():
        raise ValueError(
            f"'{s}' is not a valid (Python) identifier, see"
            + " https://docs.python.org/3/reference/lexical_analysis.html#identifiers"
            + " for details."
        )

    return s


def _validate_is_not_keyword(s: str) -> str:
    if iskeyword(s):
        raise ValueError(f"'{s}' is a Python keyword and not allowed here.")

    return s


def _validate_datetime(dt: Union[datetime, str, Any]) -> datetime:
    if isinstance(dt, datetime):
        return dt
    elif isinstance(dt, str):
        return isoparse(dt).astimezone(UTC)

    raise ValueError(f"'{dt}' not a string or datetime.")


def _validate_orcid_id(orcid_id: str):
    if len(orcid_id) == 19 and all(orcid_id[idx] == "-" for idx in [4, 9, 14]):
        check = 0
        for n in orcid_id[:4] + orcid_id[5:9] + orcid_id[10:14] + orcid_id[15:]:
            # adapted from stdnum.iso7064.mod_11_2.checksum()
            check = (2 * check + int(10 if n == "X" else n)) % 11
        if check == 1:
            return orcid_id  # valid

    raise ValueError(
        f"'{orcid_id} is not a valid ORCID iD in hyphenated groups of 4 digits."
    )


# TODO follow up on https://github.com/pydantic/pydantic/issues/8964
# to remove _serialize_datetime
def _serialize_datetime_json(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="seconds")


class Datetime(
    RootModel[
        Annotated[
            datetime,
            BeforeValidator(_validate_datetime),
            PlainSerializer(_serialize_datetime_json, when_used="json-unless-none"),
        ]
    ]
):
    """Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
    with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat).
    """

    @classmethod
    def now(cls):
        return cls(datetime.now(UTC))


class Doi(ValidatedString):
    """A digital object identifier, see https://www.doi.org/"""

    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
        Annotated[str, StringConstraints(pattern=DOI_REGEX)]
    ]


FormatVersionPlaceholder = Literal["latest", "discover"]
IdentifierAnno = Annotated[
    NotEmpty[str],
    AfterValidator(_validate_identifier),
    AfterValidator(_validate_is_not_keyword),
]


class Identifier(ValidatedString):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[IdentifierAnno]


LowerCaseIdentifierAnno = Annotated[IdentifierAnno, annotated_types.LowerCase]


class LowerCaseIdentifier(ValidatedString):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[LowerCaseIdentifierAnno]


class OrcidId(ValidatedString):
    """An ORCID identifier, see https://orcid.org/"""

    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
        Annotated[str, AfterValidator(_validate_orcid_id)]
    ]


def _normalize_multiplication(si_unit: Union[Any, str]) -> Union[Any, str]:
    if isinstance(si_unit, str):
        return si_unit.replace("×", "·").replace("*", "·").replace(" ", "·")
    else:
        return si_unit


class SiUnit(ValidatedString):
    """An SI unit"""

    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
        Annotated[
            str,
            StringConstraints(min_length=1, pattern=SI_UNIT_REGEX),
            BeforeValidator(_normalize_multiplication),
        ]
    ]


RelativeTolerance = Annotated[float, annotated_types.Interval(ge=0, le=1e-2)]
AbsoluteTolerance = Annotated[float, annotated_types.Interval(ge=0)]
MismatchedElementsPerMillion = Annotated[int, annotated_types.Interval(ge=0, le=1000)]
