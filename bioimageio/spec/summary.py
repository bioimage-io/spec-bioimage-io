from itertools import chain
from pathlib import Path
from types import MappingProxyType
from typing import (
    Any,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Tuple,
    Union,
    no_type_check,
)

import rich.console
import rich.markdown
from pydantic import BaseModel, Field, model_validator
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
    {INFO: INFO_NAME, WARNING: WARNING_NAME, ALERT: ALERT_NAME, ERROR: ERROR_NAME}
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


def format_loc(loc: Loc, enclose_in: str = "`") -> str:
    if not loc:
        loc = ("__root__",)

    loc_str = ".".join(f"({x})" if x[0].isupper() else x for x in map(str, loc))

    # additional field validation can make the location information quite convoluted, e.g.
    # `weights.pytorch_state_dict.dependencies.source.function-after[validate_url_ok(), url['http','https']]` Input should be a valid URL, relative URL without a base
    # therefore we remove the `.function-after[validate_url_ok(), url['http','https']]` here
    brief_loc_str, *_ = loc_str.split(".function-after")
    return f"{enclose_in}{brief_loc_str}{enclose_in}"


class InstalledPackage(TypedDict):
    name: str
    version: str


class ValidationContextSummary(TypedDict):
    perform_io_checks: bool
    known_files: Mapping[str, str]
    root: str
    warning_level: str


class ValidationDetail(BaseModel, extra="allow"):
    name: str
    status: Literal["passed", "failed"]
    errors: List[ErrorEntry] = Field(default_factory=list)
    warnings: List[WarningEntry] = Field(default_factory=list)
    context: Optional[ValidationContextSummary] = None

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
    type: str
    format_version: str
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

    @staticmethod
    def _format_md_table(rows: List[List[str]]) -> str:
        """format `rows` as markdown table"""
        n_cols = len(rows[0])
        assert all(len(row) == n_cols for row in rows)
        col_widths = [max(max(len(row[i]) for row in rows), 3) for i in range(n_cols)]

        lines = [" | ".join(rows[0][i].center(col_widths[i]) for i in range(n_cols))]
        lines.append(" | ".join("---".center(col_widths[i]) for i in range(n_cols)))
        lines.extend(
            [
                " | ".join(row[i].ljust(col_widths[i]) for i in range(n_cols))
                for row in rows[1:]
            ]
        )
        return "\n| " + " |\n| ".join(lines) + " |\n"

    def format(
        self,
        hide_tracebacks: bool = False,
        hide_source: bool = False,
        hide_env: bool = False,
        root_loc: Loc = (),
    ) -> str:
        info = self._format_md_table(
            [[self.status_icon, f"{self.name.strip('.').strip()} {self.status}"]]
            + ([] if hide_source else [["source", self.source_name]])
            + [
                ["format version", f"{self.type} {self.format_version}"],
            ]
            + ([] if hide_env else [[e["name"], e["version"]] for e in self.env])
        )

        def format_loc(loc: Loc):
            return "`" + (".".join(map(str, root_loc + loc)) or ".") + "`"

        details = [["❓", "location", "detail"]]
        for i, d in enumerate(self.details):
            details.append([d.status_icon, "", d.name])
            if d.context is not None:
                details.append(
                    [
                        "🔍",
                        "context.perform_io_checks",
                        str(d.context["perform_io_checks"]),
                    ]
                )
                if d.context["perform_io_checks"]:
                    details.append(["🔍", "context.root", d.context["root"]])
                    for kfn, sha in d.context["known_files"].items():
                        details.append(["🔍", f"context.known_files.{kfn}", sha])

                details.append(
                    ["🔍", "context.warning_level", d.context["warning_level"]]
                )

            for entry in d.errors:
                details.append(["❌", format_loc(entry.loc), entry.msg])
                if hide_tracebacks:
                    continue

                for tb in entry.traceback:
                    if not (tb_stripped := tb.strip()):
                        continue

                    first_tb_line, *tb_lines = tb_stripped.split("\n")
                    if (
                        first_tb_line.startswith('File "')
                        and '", line' in first_tb_line
                    ):
                        path, where = first_tb_line[len('File "') :].split('", line')
                        try:
                            p = Path(path)
                        except Exception:
                            file_name = path
                        else:
                            path = p.as_posix()
                            file_name = p.name

                        where = ", line" + where
                        first_tb_line = f'[{file_name}]({file_name} "{path}"){where}'

                    if tb_lines:
                        tb_rest = "<br>`" + "`<br>`".join(tb_lines) + "`"
                    else:
                        tb_rest = ""

                    details.append(["", "", first_tb_line + tb_rest])

            for entry in d.warnings:
                details.append(["⚠", format_loc(entry.loc), entry.msg])

            if i != len(details) - 1:
                details.append(["", "", ""])

        return f"{info}{self._format_md_table(details)}"

    # TODO: fix bug which casuses extensive white space between the info table and details table
    @no_type_check
    def display(self) -> None:
        formatted = self.format()
        try:
            from IPython.core.getipython import get_ipython
            from IPython.display import Markdown, display
        except ImportError:
            pass
        else:
            if get_ipython() is not None:
                _ = display(Markdown(formatted))
                return

        rich_markdown = rich.markdown.Markdown(formatted)
        console = rich.console.Console()
        console.print(rich_markdown)

    def add_detail(self, detail: ValidationDetail):
        if detail.status == "failed":
            self.status = "failed"
        elif detail.status != "passed":
            assert_never(detail.status)

        self.details.append(detail)
