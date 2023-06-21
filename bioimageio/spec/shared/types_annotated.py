from typing import Any, Mapping
import annotated_types
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated
from bioimageio.spec.shared.validation import (
    validate_identifier,
    validate_version,
    validate_raw_mapping,
)

Version = Annotated[str, AfterValidator(validate_version)]
CapitalStr = Annotated[str, AfterValidator(lambda s: s.capitalize())]
Sha256 = Annotated[str, annotated_types.Len(64, 64)]
NonEmptyStr = Annotated[str, annotated_types.MinLen(1)]  # common case of non-empty string
Identifier = Annotated[NonEmptyStr, AfterValidator(validate_identifier)]

# RawMappingField to use in field definitions instead of RawMapping,
# because pydantic cannot handle recursive type definitions
RawMappingField = Annotated[Mapping[str, Any], AfterValidator(validate_raw_mapping)]
