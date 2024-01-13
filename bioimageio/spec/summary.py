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
            if "severity" in data and "severity_name" not in data and data["severity"] in WARNING_SEVERITY_TO_NAME:
                data["severity_name"] = WARNING_SEVERITY_TO_NAME[data["severity"]]

            if "severity" in data and "severity_name" not in data and data["severity"] in WARNING_SEVERITY_TO_NAME:
                data["severity"] = WARNING_NAME_TO_LEVEL[data["severity_name"]]

        return data


def format_loc(loc: Loc, root: str = "root") -> str:
    if not loc:
        loc = (root,)

    return ".".join(f"({x})" if x[0].isupper() else x for x in map(str, loc))


class ValidationSummary(BaseModel):
    name: str
    source_name: str
    status: Literal["passed", "failed"]
    # status_details: Dict[str, str] = Field(default_factory=dict)
    errors: List[ErrorEntry] = Field(default_factory=list)
    traceback: List[str] = Field(default_factory=list)
    warnings: List[WarningEntry] = Field(default_factory=list)
    bioimageio_spec_version: str = VERSION

    def format(self) -> str:
        es = "".join(f"\n    {format_loc(e.loc)}: {e.msg}" for e in self.errors)
        ws = "".join(f"\n    {format_loc(w.loc)}: {w.msg}" for w in self.warnings)

        es_msg = f"\nerrors: {es}" if es else ""
        ws_msg = f"\nwarnings: {ws}" if ws else ""

        return f"{self.name.strip('.')}: {self.status}\nsource: {self.source_name}{es_msg}{ws_msg}"

    def __str__(self):
        return f"{self.__class__.__name__}:\n" + self.format()
