from typing import Any, List, Literal, Mapping, Tuple, Union

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)
from pydantic_core.core_schema import ErrorType

from bioimageio.spec._internal.constants import (
    VERSION,
    WARNING,
    WARNING_NAME,
    WARNING_NAME_TO_LEVEL,
    WARNING_SEVERITY_TO_NAME,
)
from bioimageio.spec._internal.validation_context import WarningLevel as WarningLevel
from bioimageio.spec._internal.validation_context import WarningSeverity as WarningSeverity

Loc = Tuple[Union[int, str], ...]  # location of error/warning in a nested data structure
WarningSeverityName = Literal["info", "warning", "alert"]
WarningLevelName = Literal[WarningSeverityName, "error"]


class ValidationEntry(BaseModel):
    loc: Loc
    msg: str
    type: Union[ErrorType, str]


class ErrorEntry(ValidationEntry):
    traceback: List[str] = Field(default_factory=list)


class WarningEntry(ValidationEntry):
    severity: WarningSeverity = WARNING
    severity_name: WarningSeverityName = WARNING_NAME

    @model_validator(mode="before")  # type: ignore (https://github.com/microsoft/pyright/issues/6875)
    @classmethod
    def sync_severity_with_severity_name(cls, data: Union[Mapping[Any, Any], Any]) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            assert isinstance(data, dict)
            if "severity" in data and "severity_name" not in data and data["severity"] in WARNING_SEVERITY_TO_NAME:
                data["severity_name"] = WARNING_SEVERITY_TO_NAME[data["severity"]]

            if "severity" in data and "severity_name" not in data and data["severity"] in WARNING_SEVERITY_TO_NAME:
                data["severity"] = WARNING_NAME_TO_LEVEL[data["severity_name"]]

        return data


def format_loc(loc: Loc) -> str:
    if not loc:
        loc = ("__root__",)

    return ".".join(f"({x})" if x[0].isupper() else x for x in map(str, loc))


class ValidationSummary(BaseModel):
    name: str
    source_name: str
    status: Literal["passed", "failed"]
    # status_details: Dict[str, str] = Field(default_factory=dict)
    errors: List[ErrorEntry] = Field(default_factory=list)
    warnings: List[WarningEntry] = Field(default_factory=list)
    bioimageio_spec_version: str = VERSION

    def format(self, hide_tracebacks: bool = False, hide_source: bool = False, root_loc: Loc = ()) -> str:
        indent = "      " if root_loc else ""
        src = "" if hide_source else f"\n{indent}source: {self.source_name}"
        errs_wrns = self._format_errors_and_warnings(hide_tracebacks=hide_tracebacks, root_loc=root_loc)
        return f"{indent}{self.name.strip('.')}: {self.status}{src}{errs_wrns}"

    def _format_errors_and_warnings(self, hide_tracebacks: bool, root_loc: Loc):
        indent = "      " if root_loc else ""
        if hide_tracebacks:
            tbs = [""] * len(self.errors)
        else:
            tbs = [
                ("\n      Traceback:\n      " if e.traceback else "") + "\n      ".join(e.traceback)
                for e in self.errors
            ]

        es = "".join(f"\n    {format_loc(root_loc + e.loc)}: {e.msg}{tb}" for e, tb in zip(self.errors, tbs))
        ws = "".join(f"\n    {format_loc(root_loc + w.loc)}: {w.msg}" for w in self.warnings)

        return f"\n{indent}errors: {es}" if es else "" + f"\n{indent}warnings: {ws}" if ws else ""

    def __str__(self):
        return f"{self.__class__.__name__}:\n" + self.format()
