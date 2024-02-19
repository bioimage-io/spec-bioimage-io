from __future__ import annotations

import typing
from datetime import date as _date
from datetime import datetime as _datetime

import annotated_types
from pydantic import StringConstraints as _StringConstraints
from typing_extensions import Annotated as _Annotated
from typing_extensions import TypeAliasType as _TypeAliasType

from bioimageio.spec._internal.constants import DOI_REGEX, SI_UNIT_REGEX
from bioimageio.spec._internal.types import field_validation as _fv
from bioimageio.spec._internal.types._file_source import (
    AbsoluteDirectory as AbsoluteDirectory,
)
from bioimageio.spec._internal.types._file_source import (
    AbsoluteFilePath as AbsoluteFilePath,
)
from bioimageio.spec._internal.types._file_source import FileName as FileName
from bioimageio.spec._internal.types._file_source import FileSource as FileSource
from bioimageio.spec._internal.types._file_source import HttpUrl as HttpUrl
from bioimageio.spec._internal.types._file_source import (
    ImportantFileSource as ImportantFileSource,
)
from bioimageio.spec._internal.types._file_source import (
    IncludeInPackage as IncludeInPackage,
)
from bioimageio.spec._internal.types._file_source import (
    PermissiveFileSource as PermissiveFileSource,
)
from bioimageio.spec._internal.types._file_source import (
    RelativeFilePath as RelativeFilePath,
)
from bioimageio.spec._internal.types._generated_spdx_license_type import (
    DeprecatedLicenseId as DeprecatedLicenseId,
)
from bioimageio.spec._internal.types._generated_spdx_license_type import (
    LicenseId as LicenseId,
)
from bioimageio.spec._internal.types._version import Version as Version

S = typing.TypeVar("S", bound=typing.Sequence[typing.Any])
NotEmpty = _Annotated[S, annotated_types.MinLen(1)]

Datetime = _Annotated[_datetime, _fv.BeforeValidator(_fv.validate_datetime)]
"""Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."""

Doi = typing.NewType("Doi", _Annotated[str, _StringConstraints(pattern=DOI_REGEX)])
FormatVersionPlaceholder = typing.Literal["latest", "discover"]
IdentifierStr = _Annotated[  # allows to init child NewTypes with str
    NotEmpty[str],
    _fv.AfterValidator(_fv.validate_identifier),
    _fv.AfterValidator(_fv.validate_is_not_keyword),
]
Identifier = typing.NewType("Identifier", IdentifierStr)
LowerCaseIdentifierStr = _Annotated[
    IdentifierStr, annotated_types.LowerCase
]  # allows to init child NewTypes with str
LowerCaseIdentifier = typing.NewType("LowerCaseIdentifier", LowerCaseIdentifierStr)
OrcidId = typing.NewType(
    "OrcidId", _Annotated[str, _fv.AfterValidator(_fv.validate_orcid_id)]
)
_ResourceIdAnno = _Annotated[
    NotEmpty[str],
    annotated_types.LowerCase,
    annotated_types.Predicate(lambda s: "\\" not in s and s[0] != "/" and s[-1] != "/"),
]
ResourceId = typing.NewType("ResourceId", _ResourceIdAnno)
Sha256 = typing.NewType(
    "Sha256",
    _Annotated[
        str,
        _StringConstraints(
            strip_whitespace=True, to_lower=True, min_length=64, max_length=64
        ),
    ],
)
SiUnit = typing.NewType(
    "SiUnit",
    _Annotated[
        str,
        _StringConstraints(min_length=1, pattern=SI_UNIT_REGEX),
        _fv.BeforeValidator(
            lambda s: (
                s.replace("×", "·").replace("*", "·").replace(" ", "·")
                if isinstance(s, str)
                else s
            )
        ),
    ],
)

# types as loaded from YAML 1.2 (with ruyaml)
YamlLeafValue = typing.Union[bool, _date, _datetime, float, int, str, None]
YamlKey = typing.Union[  # YAML Arrays are cast to tuples if used as key in mappings
    YamlLeafValue, typing.Tuple[YamlLeafValue, ...]  # (nesting is not allowed though)
]
# note: '_TypeAliasType' allows use of recursive type in pydantic:
#       https://docs.pydantic.dev/latest/concepts/types/#named-recursive-types
# YamlArray = _TypeAliasType("YamlArray", typing.List[YamlValue])
# YamlMapping = _TypeAliasType("YamlMapping", typing.Dict[YamlKey, YamlValue])
# YamlValue = _TypeAliasType("YamlValue", typing.Union[YamlLeafValue, YamlArray, YamlMapping])
YamlValue = _TypeAliasType(
    "YamlValue",
    typing.Union[
        YamlLeafValue, typing.List["YamlValue"], typing.Dict[YamlKey, "YamlValue"]
    ],
)

# derived types
DatasetId = typing.NewType("DatasetId", _ResourceIdAnno)
BioimageioYamlContent = typing.Dict[str, YamlValue]
BioimageioYamlSource = typing.Union[PermissiveFileSource, BioimageioYamlContent]
