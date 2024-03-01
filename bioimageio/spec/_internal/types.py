from __future__ import annotations

import typing
from datetime import datetime as _datetime

import annotated_types
from pydantic import RootModel, StringConstraints
from typing_extensions import Annotated as _Annotated

from bioimageio.spec._internal import field_validation as _fv
from bioimageio.spec._internal._version_type import Version as Version
from bioimageio.spec._internal.constants import DOI_REGEX, SI_UNIT_REGEX
from bioimageio.spec._internal.io import FileSource as FileSource
from bioimageio.spec._internal.io import HttpUrl as HttpUrl
from bioimageio.spec._internal.io import (
    ImportantFileSource as ImportantFileSource,
)
from bioimageio.spec._internal.io import (
    IncludeInPackage as IncludeInPackage,
)
from bioimageio.spec._internal.io import (
    PermissiveFileSource as PermissiveFileSource,
)
from bioimageio.spec._internal.io import (
    RelativeFilePath as RelativeFilePath,
)
from bioimageio.spec._internal.io_basics import (
    AbsoluteDirectory as AbsoluteDirectory,
)
from bioimageio.spec._internal.io_basics import (
    AbsoluteFilePath as AbsoluteFilePath,
)
from bioimageio.spec._internal.io_basics import FileName as FileName
from bioimageio.spec._internal.types._license_type import (
    DeprecatedLicenseId as DeprecatedLicenseId,
)
from bioimageio.spec._internal.types._license_type import LicenseId as LicenseId

S = typing.TypeVar("S", bound=typing.Sequence[typing.Any])
NotEmpty = _Annotated[S, annotated_types.MinLen(1)]

Datetime = _Annotated[_datetime, _fv.BeforeValidator(_fv.validate_datetime)]
"""Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."""

Doi = typing.NewType("Doi", _Annotated[str, StringConstraints(pattern=DOI_REGEX)])
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
SiUnit = typing.NewType(
    "SiUnit",
    _Annotated[
        str,
        StringConstraints(min_length=1, pattern=SI_UNIT_REGEX),
        _fv.BeforeValidator(
            lambda s: (
                s.replace("×", "·").replace("*", "·").replace(" ", "·")
                if isinstance(s, str)
                else s
            )
        ),
    ],
)

# derived types
ApplicationId = typing.NewType("ApplicationId", _ResourceIdAnno)
CollectionId = typing.NewType("CollectionId", _ResourceIdAnno)
DatasetId = typing.NewType("DatasetId", _ResourceIdAnno)
ModelId = typing.NewType("ModelId", _ResourceIdAnno)
NotebookId = typing.NewType("NotebookId", _ResourceIdAnno)
