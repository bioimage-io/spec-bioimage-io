from typing import TypeVar
import annotated_types
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated
from bioimageio.spec.shared.validation import (
    validate_identifier,
    validate_version,
)

T = TypeVar("T")

NonEmpty = Annotated[T, annotated_types.MinLen(1)]  # common case of non-empty sequence
Sha256 = Annotated[str, annotated_types.Len(64, 64)]
Version = Annotated[str, AfterValidator(validate_version)]

# derived
CapitalStr = Annotated[NonEmpty[str], AfterValidator(lambda s: s.capitalize())]
Identifier = Annotated[NonEmpty[str], AfterValidator(validate_identifier)]
