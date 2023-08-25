import collections.abc
from typing import Any, Dict, List, Literal, Mapping, Union

from pydantic import BaseModel, Field, model_validator
from pydantic_core.core_schema import ErrorType

from bioimageio.spec import __version__
from bioimageio.spec._internal.constants import NAME_TO_SEVERITY, SEVERITY_TO_NAME, WARNING, WARNING_NAME
from bioimageio.spec.types import Loc, Severity, SeverityName


class ValidationEntry(BaseModel):
    loc: Loc
    msg: str
    type: Union[ErrorType, str]


class ErrorEntry(ValidationEntry):
    pass


class WarningEntry(ValidationEntry):
    severity: Severity = WARNING
    severity_name: SeverityName = WARNING_NAME

    @model_validator(mode="before")
    @classmethod
    def sync_severity_with_severity_name(cls, data: Union[Mapping[Any, Any], Any]) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            assert isinstance(data, dict)
            if "severity" in data and not "severity_name" in data and data["severity"] in SEVERITY_TO_NAME:
                data["severity_name"] = SEVERITY_TO_NAME[data["severity"]]

            if "severity" in data and not "severity_name" in data and data["severity"] in SEVERITY_TO_NAME:
                data["severity"] = NAME_TO_SEVERITY[data["severity_name"]]

        return data


class ValidationSummary(BaseModel):
    name: str
    source_name: str
    status: Literal["passed", "failed"]
    # status_details: Dict[str, str] = Field(default_factory=dict)
    errors: List[ErrorEntry] = Field(default_factory=list)
    traceback: List[str] = Field(default_factory=list)
    warnings: List[WarningEntry] = Field(default_factory=list)
    bioimageio_spec_version: str = __version__
