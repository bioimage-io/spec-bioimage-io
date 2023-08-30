from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Literal, Sequence, Tuple, TypeVar, Union

import annotated_types
from pydantic import HttpUrl, StringConstraints
from typing_extensions import Annotated

from bioimageio.spec._internal.constants import SI_UNIT_REGEX
from bioimageio.spec._internal.field_validation import AfterValidator, BeforeValidator, Predicate
from bioimageio.spec._internal.field_validation import RelativeFilePath as RelativeFilePath
from bioimageio.spec._internal.field_validation import RestrictCharacters
from bioimageio.spec._internal.field_validation import ValidationContext as ValidationContext
from bioimageio.spec._internal.field_validation import (
    capitalize_first_letter,
    validate_datetime,
    validate_identifier,
    validate_is_not_keyword,
    validate_orcid_id,
    validate_unique_entries,
    validate_version,
)
from bioimageio.spec._internal.generated_spdx_license_type import DeprecatedLicenseId as DeprecatedLicenseId
from bioimageio.spec._internal.generated_spdx_license_type import LicenseId as LicenseId

T = TypeVar("T")
S = TypeVar("S", bound=Sequence[Any])

# types to describe RDF as pydantic models
NonEmpty = Annotated[S, annotated_types.MinLen(1)]

AxesStr = Annotated[str, RestrictCharacters("bitczyx"), AfterValidator(validate_unique_entries)]
AxesInCZYX = Annotated[str, RestrictCharacters("czyx"), AfterValidator(validate_unique_entries)]
CapitalStr = Annotated[NonEmpty[str], AfterValidator(capitalize_first_letter)]
Datetime = Annotated[datetime, BeforeValidator(validate_datetime)]
"""Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."""
Identifier = Annotated[
    NonEmpty[str],
    AfterValidator(validate_identifier),
    AfterValidator(validate_is_not_keyword),
]
LowerCaseIdentifier = Annotated[Identifier, Predicate(str.islower)]
FileName = str
FileSource = Union[HttpUrl, RelativeFilePath]
OrcidId = Annotated[str, AfterValidator(validate_orcid_id)]
Sha256 = Annotated[str, annotated_types.Len(64, 64)]
SiUnit = Annotated[
    str,
    StringConstraints(min_length=1, pattern=SI_UNIT_REGEX),
    BeforeValidator(lambda s: s.replace("×", "·").replace("*", "·").replace(" ", "·") if isinstance(s, str) else s),
]
Unit = Union[Literal["px", "arbitrary intensity"], SiUnit]
UniqueTuple = Annotated[Tuple[T], AfterValidator(validate_unique_entries)]
Version = Annotated[str, AfterValidator(validate_version)]

# types for validation logic
FormatVersionPlaceholder = Literal["latest", "discover"]
Loc = Tuple[Union[int, str], ...]  # location of error/warning in a nested data structure
WarningSeverity = Literal[20, 30, 35]
WarningSeverityName = Literal["info", "warning", "alert"]
WarningLevel = Literal[WarningSeverity, 50]
"""With warning level x validation warnings of severity >=x are raised.
Highest warning level 50/error does not raise any validaiton warnings (only validation errors)."""
WarningLevelName = Literal[WarningSeverityName, "error"]

# types as loaded from YAML 1.2 (with ruamel.yaml)
YamlLeafValue = Union[bool, date, datetime, float, int, str, None]
YamlArray = List["YamlValue"]  # YAML Array is cast to list, but...
YamlKey = Union[  # ... YAML Arrays are cast to tuples if used as key in mappings
    YamlLeafValue, Tuple[YamlLeafValue, ...]  # (nesting is not allowed though)
]
YamlMapping = Dict[YamlKey, "YamlValue"]  # YAML Mappings are cast to dict
YamlValue = Union[YamlLeafValue, YamlArray, YamlMapping]
