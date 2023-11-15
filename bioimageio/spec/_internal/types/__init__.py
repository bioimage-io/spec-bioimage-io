from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Literal, NewType, Sequence, Tuple, TypeVar, Union

import annotated_types
from pydantic import StringConstraints
from typing_extensions import Annotated

from bioimageio.spec._internal.constants import DOI_REGEX, SI_UNIT_REGEX
from bioimageio.spec._internal.types._file_source import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec._internal.types._file_source import FileName as FileName
from bioimageio.spec._internal.types._file_source import FileSource as FileSource
from bioimageio.spec._internal.types._file_source import HttpUrl as HttpUrl
from bioimageio.spec._internal.types._file_source import PermissiveFileSource as PermissiveFileSource
from bioimageio.spec._internal.types._file_source import RelativeFilePath as RelativeFilePath
from bioimageio.spec._internal.types._file_source import StrictFileSource as StrictFileSource
from bioimageio.spec._internal.types._generated_spdx_license_type import DeprecatedLicenseId as DeprecatedLicenseId
from bioimageio.spec._internal.types._generated_spdx_license_type import LicenseId as LicenseId
from bioimageio.spec._internal.types._version import Version as Version
from bioimageio.spec._internal.types.field_validation import (
    AfterValidator,
    BeforeValidator,
    validate_datetime,
    validate_identifier,
    validate_is_not_keyword,
    validate_orcid_id,
)

S = TypeVar("S", bound=Sequence[Any])
NotEmpty = Annotated[S, annotated_types.MinLen(1)]

Datetime = Annotated[datetime, BeforeValidator(validate_datetime)]
"""Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."""

Doi = NewType("Doi", Annotated[str, StringConstraints(pattern=DOI_REGEX)])
FormatVersionPlaceholder = Literal["latest", "discover"]
IdentifierStr = Annotated[  # allows to init child NewTypes with str
    NotEmpty[str],
    AfterValidator(validate_identifier),
    AfterValidator(validate_is_not_keyword),
]
Identifier = NewType("Identifier", IdentifierStr)
LowerCaseIdentifierStr = Annotated[IdentifierStr, annotated_types.LowerCase]  # allows to init child NewTypes with str
LowerCaseIdentifier = NewType("LowerCaseIdentifier", LowerCaseIdentifierStr)
OrcidId = NewType("OrcidId", Annotated[str, AfterValidator(validate_orcid_id)])
ResourceId = NewType(
    "ResourceId",
    Annotated[
        NotEmpty[str],
        annotated_types.LowerCase,
        annotated_types.Predicate(lambda s: "\\" not in s and s[0] != "/" and s[-1] != "/"),
    ],
)
Sha256 = NewType(
    "Sha256",
    Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, min_length=64, max_length=64)],
)
SiUnit = NewType(
    "SiUnit",
    Annotated[
        str,
        StringConstraints(min_length=1, pattern=SI_UNIT_REGEX),
        BeforeValidator(lambda s: s.replace("×", "·").replace("*", "·").replace(" ", "·") if isinstance(s, str) else s),
    ],
)
Unit = Union[Literal["arbitrary unit", "px"], SiUnit]

# types as loaded from YAML 1.2 (with ruamel.yaml)
YamlLeafValue = Union[bool, date, datetime, float, int, str, None]
YamlKey = Union[  # YAML Arrays are cast to tuples if used as key in mappings
    YamlLeafValue, Tuple[YamlLeafValue, ...]  # (nesting is not allowed though)
]
YamlArray = List["YamlValue"]
YamlMapping = Dict[YamlKey, "YamlValue"]
# note: for use in pydantic see https://docs.pydantic.dev/latest/concepts/types/#named-recursive-types
#   and don't open another issue a la https://github.com/pydantic/pydantic/issues/8021
YamlValue = Union[YamlLeafValue, YamlArray, YamlMapping]

# derived types
DatasetId = NewType("DatasetId", ResourceId)
BioimageioYamlContent = Dict[str, YamlValue]
