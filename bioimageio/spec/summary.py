from typing import Any, List, Literal, Mapping, Union

from pydantic import model_validator  # type: ignore
from pydantic import BaseModel, Field
from pydantic_core.core_schema import ErrorType

from bioimageio.spec import __version__
from bioimageio.spec._internal.constants import (
    WANRING_NAME_TO_SEVERITY,
    WARNING,
    WARNING_NAME,
    WARNING_SEVERITY_TO_NAME,
)
from bioimageio.spec.types import Loc, WarningSeverity, WarningSeverityName


class ValidationEntry(BaseModel):
    loc: Loc
    msg: str
    type: Union[ErrorType, str]


class ErrorEntry(ValidationEntry):
    pass


class WarningEntry(ValidationEntry):
    severity: WarningSeverity = WARNING
    severity_name: WarningSeverityName = WARNING_NAME

    @model_validator(mode="before")
    @classmethod
    def sync_severity_with_severity_name(cls, data: Union[Mapping[Any, Any], Any]) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            assert isinstance(data, dict)
            if "severity" in data and not "severity_name" in data and data["severity"] in WARNING_SEVERITY_TO_NAME:
                data["severity_name"] = WARNING_SEVERITY_TO_NAME[data["severity"]]

            if "severity" in data and not "severity_name" in data and data["severity"] in WARNING_SEVERITY_TO_NAME:
                data["severity"] = WANRING_NAME_TO_SEVERITY[data["severity_name"]]

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

    @staticmethod
    def _format_loc(loc: Loc) -> str:
        if not loc:
            loc = ("root",)

        return ".".join(f"({x})" if x[0].isupper() else x for x in map(str, loc))

    def format(self) -> str:
        es = "\n    ".join(f"{self._format_loc(e.loc)}: {e.msg}" for e in self.errors)
        ws = "\n    ".join(f"{self._format_loc(w.loc)}: {w.msg}" for w in self.warnings)

        es_msg = f"errors: {es}" if es else ""
        ws_msg = f"warnings: {ws}" if ws else ""

        return f"{self.name.strip('.')}: {self.status}\nsource: {self.source_name}\n{es_msg}\n{ws_msg}"
