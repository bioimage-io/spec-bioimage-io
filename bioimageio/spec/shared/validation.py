from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union
from pydantic import HttpUrl

from pydantic_core.core_schema import ErrorType
from typing_extensions import NotRequired, TypedDict

from bioimageio.spec._internal._warn import WarningType


@dataclass(frozen=True)
class ValidationContext:
    root: Union[HttpUrl, Path] = Path()  # url/path serving as base to any relative file paths.


class ValidationOutcome(TypedDict):
    loc: Tuple[Union[int, str], ...]
    msg: str


class ValidationError(ValidationOutcome):
    type: Union[ErrorType, str]


class ValidationWarning(ValidationOutcome):
    type: WarningType


class ValidationSummary(TypedDict):
    bioimageio_spec_version: str
    error: Union[str, Sequence[ValidationError], None]
    name: str
    source_name: str
    status: Union[Literal["passed", "failed"], str]
    traceback: NotRequired[Sequence[str]]
    warnings: NotRequired[Sequence[ValidationWarning]]


class LegacyValidationSummary(TypedDict):
    bioimageio_spec_version: str
    error: Union[None, str, Dict[str, Any]]
    name: str
    nested_errors: NotRequired[Dict[str, Dict[str, Any]]]
    source_name: str
    status: Union[Literal["passed", "failed"], str]
    traceback: Optional[List[str]]
    warnings: Dict[str, Any]
