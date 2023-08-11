from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Sequence, Tuple, Union

from pydantic import AnyUrl, DirectoryPath
from pydantic_core.core_schema import ErrorType
from typing_extensions import NotRequired, TypedDict

from bioimageio.spec._internal._constants import ERROR

if TYPE_CHECKING:
    from bioimageio.spec.shared.types import WarningLevel, WarningLevelName


class ValidationContext(TypedDict):
    root: NotRequired[Union[DirectoryPath, AnyUrl]]
    """url/path serving as base to any relative file paths. Default provided as data field `root`.0"""

    warning_level: NotRequired[WarningLevel]
    """raise warnings of severity s as validation errors if s >= `warning_level`"""


class ValContext(TypedDict):
    """internally used validation context"""

    root: Union[DirectoryPath, AnyUrl]
    """url/path serving as base to any relative file paths. Default provided as data field `root`.0"""

    warning_level: WarningLevel
    """raise warnings of severity s as validation errors if s >= `warning_level`"""

    original_format: NotRequired[Tuple[int, int, int]]
    """original format version of the validation data (set dynamically during validation of resource descriptions)."""

    collection_base_content: NotRequired[Dict[str, Any]]
    """Collection base content (set dynamically during validation of collection resource descriptions)."""


def get_validation_context(
    root: Union[DirectoryPath, AnyUrl] = Path(), warning_level: WarningLevel = ERROR
) -> ValContext:
    return ValContext(root=root, warning_level=warning_level)


class ValidationOutcome(TypedDict):
    loc: Tuple[Union[int, str], ...]
    msg: str


class ValidationError(ValidationOutcome):
    type: Union[ErrorType, str]


class ValidationWarning(ValidationOutcome):
    type: WarningLevelName


class ValidationSummary(TypedDict):
    bioimageio_spec_version: str
    name: str
    source_name: str
    status: Union[Literal["passed", "failed"], str]
    errors: Sequence[ValidationError]
    traceback: NotRequired[Sequence[str]]
    warnings: Sequence[ValidationWarning]


class LegacyValidationSummary(TypedDict):
    bioimageio_spec_version: str
    error: Union[None, str, Dict[str, Any]]
    name: str
    nested_errors: NotRequired[Dict[str, Dict[str, Any]]]
    source_name: str
    status: Union[Literal["passed", "failed"], str]
    traceback: Optional[List[str]]
    warnings: Dict[str, Any]
