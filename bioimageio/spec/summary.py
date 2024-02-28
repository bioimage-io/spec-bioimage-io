from itertools import chain
from typing import Any, List, Literal, Mapping, Tuple, Union

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)
from pydantic_core.core_schema import ErrorType
from typing_extensions import TypedDict, assert_never

from bioimageio.spec._internal.constants import (
    VERSION,
    WARNING,
    WARNING_NAME,
    WARNING_NAME_TO_LEVEL,
    WARNING_SEVERITY_TO_NAME,
)
from bioimageio.spec._internal.validation_context import WarningLevel as WarningLevel
from bioimageio.spec._internal.validation_context import (
    WarningSeverity as WarningSeverity,
)

Loc = Tuple[
    Union[int, str], ...
]  # location of error/warning in a nested data structure
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

    @model_validator(mode="before")
    @classmethod
    def sync_severity_with_severity_name(
        cls, data: Union[Mapping[Any, Any], Any]
    ) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            assert isinstance(data, dict)
            if (
                "severity" in data
                and "severity_name" not in data
                and data["severity"] in WARNING_SEVERITY_TO_NAME
            ):
                data["severity_name"] = WARNING_SEVERITY_TO_NAME[data["severity"]]

            if (
                "severity" in data
                and "severity_name" not in data
                and data["severity"] in WARNING_SEVERITY_TO_NAME
            ):
                data["severity"] = WARNING_NAME_TO_LEVEL[data["severity_name"]]

        return data


def format_loc(loc: Loc) -> str:
    if not loc:
        loc = ("__root__",)

    ret = ".".join(f"({x})" if x[0].isupper() else x for x in map(str, loc))
    #  additional field validation can make the location information quite convoluted, e.g.
    # weights.pytorch_state_dict.dependencies.source.function-after[validate_url_ok(), url['http','https']]: Input should be a valid URL, relative URL without a base
    # therefore we remove the `.function-after[validate_url_ok(), url['http','https']]` here
    real_loc, *_ = ret.split(".function-after")  # remove validation func names from loc
    return real_loc


class InstalledPackage(TypedDict):
    name: str
    version: str


class ValidationDetail(BaseModel, extra="allow"):
    name: str
    status: Literal["passed", "failed"]
    errors: List[ErrorEntry] = Field(default_factory=list)
    warnings: List[WarningEntry] = Field(default_factory=list)

    def __str__(self):
        return f"{self.__class__.__name__}:\n" + self.format()

    @property
    def status_icon(self):
        if self.status == "passed":
            return "✔️"
        else:
            return "❌"

    def format(self, hide_tracebacks: bool = False, root_loc: Loc = ()) -> str:
        indent = "      " if root_loc else ""
        errs_wrns = self._format_errors_and_warnings(
            hide_tracebacks=hide_tracebacks, root_loc=root_loc
        )
        return f"{indent}{self.status_icon} {self.name.strip('.')}: {self.status}{errs_wrns}"

    def _format_errors_and_warnings(self, hide_tracebacks: bool, root_loc: Loc):
        indent = "      " if root_loc else ""
        if hide_tracebacks:
            tbs = [""] * len(self.errors)
        else:
            tbs = [
                ("\n      Traceback:\n      " if e.traceback else "")
                + "\n      ".join(e.traceback)
                for e in self.errors
            ]

        es = "".join(
            f"\n    {format_loc(root_loc + e.loc)}: {e.msg}{tb}"
            for e, tb in zip(self.errors, tbs)
        )
        ws = "".join(
            f"\n    {format_loc(root_loc + w.loc)}: {w.msg}" for w in self.warnings
        )

        return (
            f"\n{indent}errors: {es}"
            if es
            else "" + f"\n{indent}warnings: {ws}" if ws else ""
        )


class ValidationSummary(BaseModel, extra="allow"):
    name: str
    source_name: str
    status: Literal["passed", "failed"]
    details: List[ValidationDetail]
    env: List[InstalledPackage] = Field(
        default_factory=lambda: [
            InstalledPackage(name="bioimageio.spec", version=VERSION)
        ]
    )
    """list of selected, relevant package versions"""

    @property
    def status_icon(self):
        if self.status == "passed":
            return "✔️"
        else:
            return "❌"

    @property
    def errors(self) -> List[ErrorEntry]:
        return list(chain.from_iterable(d.errors for d in self.details))

    @property
    def warnings(self) -> List[WarningEntry]:
        return list(chain.from_iterable(d.warnings for d in self.details))

    def __str__(self):
        return f"{self.__class__.__name__}:\n" + self.format()

    def format(
        self,
        hide_tracebacks: bool = False,
        hide_source: bool = False,
        root_loc: Loc = (),
    ) -> str:
        indent = "   " if root_loc else ""
        src = "" if hide_source else f"\n{indent}source: {self.source_name}"
        details = f"\n{indent}" + f"\n{indent}".join(
            d.format(hide_tracebacks=hide_tracebacks, root_loc=root_loc)
            for d in self.details
        )
        return f"{indent}{self.status_icon} {self.name.strip('.')}: {self.status}{src}{details}"

    def add_detail(self, detail: ValidationDetail):
        if detail.status == "failed":
            self.status = "failed"
        elif detail.status != "passed":
            assert_never(detail.status)

        self.details.append(detail)
