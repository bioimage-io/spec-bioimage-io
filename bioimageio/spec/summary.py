from itertools import chain
from types import MappingProxyType
from typing import Any, Iterable, List, Literal, Mapping, Tuple, Union

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)
from pydantic_core.core_schema import ErrorType
from typing_extensions import TypedDict, assert_never

from ._internal.constants import VERSION
from ._internal.warning_levels import (
    ALERT,
    ALERT_NAME,
    ERROR,
    ERROR_NAME,
    INFO,
    INFO_NAME,
    WARNING,
    WARNING_NAME,
    WarningLevel,
    WarningSeverity,
)

Loc = Tuple[Union[int, str], ...]
"""location of error/warning in a nested data structure"""

WarningSeverityName = Literal["info", "warning", "alert"]
WarningLevelName = Literal[WarningSeverityName, "error"]

WARNING_SEVERITY_TO_NAME: Mapping[WarningSeverity, WarningSeverityName] = (
    MappingProxyType({INFO: INFO_NAME, WARNING: WARNING_NAME, ALERT: ALERT_NAME})
)
WARNING_LEVEL_TO_NAME: Mapping[WarningLevel, WarningLevelName] = MappingProxyType(
    {**WARNING_SEVERITY_TO_NAME, ERROR: ERROR_NAME}
)
WARNING_NAME_TO_LEVEL: Mapping[WarningLevelName, WarningLevel] = MappingProxyType(
    {v: k for k, v in WARNING_LEVEL_TO_NAME.items()}
)


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

    loc_str = ".".join(f"({x})" if x[0].isupper() else x for x in map(str, loc))

    # additional field validation can make the location information quite convoluted, e.g.
    # `weights.pytorch_state_dict.dependencies.source.function-after[validate_url_ok(), url['http','https']]` Input should be a valid URL, relative URL without a base
    # therefore we remove the `.function-after[validate_url_ok(), url['http','https']]` here
    brief_loc_str, *_ = loc_str.split(".function-after")
    return f"`{brief_loc_str}`"


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
        indent = "    " if root_loc else ""
        errs_wrns = self._format_errors_and_warnings(
            hide_tracebacks=hide_tracebacks, root_loc=root_loc
        )
        return f"{indent}{self.status_icon} {self.name.strip('.')}: {self.status}{errs_wrns}"

    def _format_errors_and_warnings(self, hide_tracebacks: bool, root_loc: Loc):
        indent = "    " if root_loc else ""
        if hide_tracebacks:
            tbs = [""] * len(self.errors)
        else:
            tbs = [
                ("\n      Traceback:\n      " if e.traceback else "")
                + "\n      ".join(e.traceback)
                for e in self.errors
            ]

        def join_parts(parts: Iterable[Tuple[str, str]]):
            last_loc = None
            lines: List[str] = []
            for loc, msg in parts:
                if loc == last_loc:
                    lines.append(f"\n  {loc} {msg}")
                else:
                    lines.append(f"\n- {loc} {msg}")

                last_loc = loc

            return "".join(lines)

        es = join_parts(
            (format_loc(root_loc + e.loc), f"{e.msg}{tb}")
            for e, tb in zip(self.errors, tbs)
        )
        ws = join_parts((format_loc(root_loc + w.loc), w.msg) for w in self.warnings)

        return (
            f"\n{indent}errors:\n{es}"
            if es
            else "" + f"\n{indent}warnings:\n{ws}" if ws else ""
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

    def _format_env(self):
        if not self.env:
            return ""

        package_w = max(len(p) for p in [e["name"] for e in self.env] + ["package"])
        version_w = max(len(v) for v in [e["version"] for e in self.env] + ["version"])

        return (
            "\n"
            f"| {'package'.center(package_w)} | {'version'.center(version_w)} |\n"
            f"| {'---'.center(package_w)} | {'---'.center(version_w)} |\n"
        ) + "".join(
            f"| {e['name'].ljust(package_w)} | {e['version'].ljust(version_w)} |\n"
            for e in self.env
        )

    def format(
        self,
        hide_tracebacks: bool = False,
        hide_source: bool = False,
        hide_env: bool = False,
        root_loc: Loc = (),
    ) -> str:
        indent = "   " if root_loc else ""
        src = "" if hide_source else f"\n{indent}source: {self.source_name}"
        env = "" if hide_env else self._format_env()
        details = f"\n{indent}" + f"\n{indent}".join(
            d.format(hide_tracebacks=hide_tracebacks, root_loc=root_loc)
            for d in self.details
        )
        return f"{indent}{self.status_icon} {self.name.strip('.')}: {self.status}{src}{env}{details}"

    def add_detail(self, detail: ValidationDetail):
        if detail.status == "failed":
            self.status = "failed"
        elif detail.status != "passed":
            assert_never(detail.status)

        self.details.append(detail)
