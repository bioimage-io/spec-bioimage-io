import os
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

from pydantic import AnyUrl, BaseModel, DirectoryPath
from typing_extensions import TypedDict

from bioimageio.spec._internal.constants import (
    BIOIMAGEIO_PERFORM_IO_CHECKS_ENV_NAME,
    ERROR,
    TRUE_ENV_VAR,
    WARNING_LEVEL_CONTEXT_KEY,
)

WarningSeverity = Literal[20, 30, 35]
WarningLevel = Literal[WarningSeverity, 50]
"""With warning level x validation warnings of severity >=x are raised.
Highest warning level 50/error does not raise any validaiton warnings (only validation errors)."""


class ValidationContext(BaseModel):
    root: Union[DirectoryPath, AnyUrl] = Path()
    """url/directory serving as base to resolve any relative file paths"""

    file_name: str = "bioimageio.yaml"
    """file name of the bioimageio Yaml file"""

    perform_io_checks: bool = os.getenv(BIOIMAGEIO_PERFORM_IO_CHECKS_ENV_NAME, "true").lower() in TRUE_ENV_VAR
    """wether or not to perfrom validation that requires IO operations like download or reading a file from disk"""


class InternalValidationContext(TypedDict):
    """internally used validation context"""

    root: Union[DirectoryPath, AnyUrl]
    """url/path serving as base to any relative file paths"""

    file_name: str
    """the file name of the RDF used only for reporting"""

    warning_level: WarningLevel
    """raise warnings of severity s as validation errors if s >= `warning_level`"""

    perform_io_checks: bool
    """wether or not to perfrom validation that requires IO operations like download or reading a file from disk"""


def create_internal_validation_context(
    given_context: Union[ValidationContext, InternalValidationContext, Dict[str, Any], None] = None,
    root: Union[DirectoryPath, AnyUrl, None] = None,  # option to overwrite given context
    file_name: Optional[str] = None,  # option to overwrite given context
    warning_level: Optional[WarningLevel] = None,  # option to overwrite given context
    perform_io_checks: Optional[bool] = None,  # option to overwrite given context
):
    if given_context is None:
        given_context = {}
    elif isinstance(given_context, ValidationContext):
        given_context = given_context.model_dump(mode="python")

    default = ValidationContext()
    return InternalValidationContext(
        root=root or given_context.get("root", default.root),
        file_name=file_name or given_context.get("file_name", default.file_name),
        warning_level=warning_level or given_context.get(WARNING_LEVEL_CONTEXT_KEY, ERROR),
        perform_io_checks=perform_io_checks
        if perform_io_checks is not None
        else given_context.get("perform_io_checks", default.perform_io_checks),
    )
