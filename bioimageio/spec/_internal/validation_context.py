from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

from pydantic import AnyUrl, BaseModel, DirectoryPath
from typing_extensions import NotRequired, TypedDict

from bioimageio.spec._internal.constants import ERROR, WARNING_LEVEL_CONTEXT_KEY
from bioimageio.spec._internal.types._version import Version

WarningSeverity = Literal[20, 30, 35]
WarningLevel = Literal[WarningSeverity, 50]
"""With warning level x validation warnings of severity >=x are raised.
Highest warning level 50/error does not raise any validaiton warnings (only validation errors)."""


class ValidationContext(BaseModel):
    root: Union[DirectoryPath, AnyUrl] = Path()
    """url/directory serving as base to resolve any relative file paths."""

    file_name: str = "rdf.bioimageio.yaml"
    """The file name of the RDF"""


class InternalValidationContext(TypedDict):
    """internally used validation context"""

    root: Union[DirectoryPath, AnyUrl]
    """url/path serving as base to any relative file paths. Default provided as data field `root`.0"""

    file_name: str
    """The file name of the RDF used only for reporting"""

    warning_level: WarningLevel
    """raise warnings of severity s as validation errors if s >= `warning_level`"""

    original_format: NotRequired[Version]
    """original format version of the validation data (set dynamically during validation of resource descriptions)."""

    collection_base_content: NotRequired[Dict[str, Any]]
    """Collection base content (set dynamically during validation of collection resource descriptions)."""


def get_internal_validation_context(
    given_context: Union[ValidationContext, InternalValidationContext, Dict[str, Any], None] = None,
    root: Union[DirectoryPath, AnyUrl, None] = None,  # option to overwrite given context
    file_name: Optional[str] = None,  # option to overwrite given context
    warning_level: Optional[WarningLevel] = None,  # option to overwrite given context
):
    if given_context is None:
        given_context = {}
    elif isinstance(given_context, ValidationContext):
        given_context = given_context.model_dump(mode="python")

    ret = InternalValidationContext(
        root=root or given_context.get("root", Path()),
        file_name=file_name or given_context.get("file_name", "rdf.bioimageio.yaml"),
        warning_level=warning_level or given_context.get(WARNING_LEVEL_CONTEXT_KEY, ERROR),
    )
    for k in {"original_format", "collection_base_content"}:  # TypedDict.__optional_keys__ requires py>=3.9
        if k in given_context:
            ret[k] = given_context[k]

    return ret
