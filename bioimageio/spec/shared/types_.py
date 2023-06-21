from typing import Mapping, Sequence, TypeVar, Union

import annotated_types
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from bioimageio.spec.shared.validation import (
    validate_identifier,
    validate_version,
)

from ._generated_spdx_license_type import LicenseId

T = TypeVar("T")

NonEmpty = Annotated[T, annotated_types.MinLen(1)]  # common case of non-empty sequence


CapitalStr = Annotated[NonEmpty[str], AfterValidator(lambda s: s.capitalize())]
Identifier = Annotated[NonEmpty[str], AfterValidator(validate_identifier)]
LicenseId = LicenseId
RawLeafValue = Union[int, float, str, bool, None]
RawMapping = Mapping[str, "RawValue"]
RawSequence = Sequence["RawValue"]
RawValue = Union[RawLeafValue, RawSequence, RawMapping]
Sha256 = Annotated[str, annotated_types.Len(64, 64)]
Version = Annotated[str, AfterValidator(validate_version)]
