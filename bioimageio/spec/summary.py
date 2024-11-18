import subprocess
from io import StringIO
from itertools import chain
from pathlib import Path
from tempfile import TemporaryDirectory
from types import MappingProxyType
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    no_type_check,
)

import rich.console
import rich.markdown
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import ErrorType
from typing_extensions import TypedDict, assert_never

from ._internal.constants import VERSION
from ._internal.io import is_yaml_value
from ._internal.io_utils import write_yaml
from ._internal.type_guards import is_mapping
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
from .conda_env import CondaEnv

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
    """Base of `ErrorEntry` and `WarningEntry`"""

    loc: Loc
    msg: str
    type: Union[ErrorType, str]


class ErrorEntry(ValidationEntry):
    """An error in a `ValidationDetail`"""

    traceback: List[str] = Field(default_factory=list)


class WarningEntry(ValidationEntry):
    """A warning in a `ValidationDetail`"""

    severity: WarningSeverity = WARNING
    severity_name: WarningSeverityName = WARNING_NAME

    @model_validator(mode="before")
    @classmethod
    def sync_severity_with_severity_name(
        cls, data: Union[Mapping[Any, Any], Any]
    ) -> Any:
        if is_mapping(data):
            data = dict(data)
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
    """helper to format a location tuple `Loc` as Markdown string"""
    if not loc:
        loc = ("__root__",)

    loc_str = ".".join(f"({x})" if x[0].isupper() else x for x in map(str, loc))

    # additional field validation can make the location information quite convoluted, e.g.
    # `weights.pytorch_state_dict.dependencies.source.function-after[validate_url_ok(), url['http','https']]` Input should be a valid URL, relative URL without a base
    # therefore we remove the `.function-after[validate_url_ok(), url['http','https']]` here
    brief_loc_str, *_ = loc_str.split(".function-after")
    return f"{enclose_in}{brief_loc_str}{enclose_in}"


class InstalledPackage(NamedTuple):
    name: str
    version: str
    build: str = ""
    channel: str = ""


class ValidationContextSummary(TypedDict):
    perform_io_checks: bool
    known_files: Mapping[str, str]
    root: str
    warning_level: str


class ValidationDetail(BaseModel, extra="allow"):
    """a detail in a validation summary"""

    name: str
    status: Literal["passed", "failed"]
    loc: Loc = ()
    """location in the RDF that this detail applies to"""
    errors: List[ErrorEntry] = Field(default_factory=list)
    warnings: List[WarningEntry] = Field(default_factory=list)
    context: Optional[ValidationContextSummary] = None

    recommended_env: Optional[CondaEnv] = None
    """recommended conda environemnt for this validation detail"""
    conda_compare: Optional[str] = None
    """output of `conda compare <recommended env>`"""

    def model_post_init(self, __context: Any):
        """create `conda_compare` default value if needed"""
        super().model_post_init(__context)
        if self.recommended_env is None or self.conda_compare is not None:
            return

        dumped_env = self.recommended_env.model_dump(mode="json")
        if not is_yaml_value(dumped_env):
            self.conda_compare = "Failed to dump recommended env to valid yaml"
            return

        with TemporaryDirectory() as d:
            path = Path(d) / "env.yaml"
            with path.open("w", encoding="utf-8") as f:
                write_yaml(dumped_env, f)

            compare_proc = subprocess.run(
                ["conda", "compare", str(path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
            )
            self.conda_compare = (
                compare_proc.stdout
                or f"conda compare exited with {compare_proc.returncode}"
            )

    def __str__(self):
        return f"{self.__class__.__name__}:\n" + self.format()

    @property
    def status_icon(self):
        if self.status == "passed":
            return "✔️"
        else:
            return "❌"

    def format(self, hide_tracebacks: bool = False, root_loc: Loc = ()) -> str:
        """format as Markdown string"""
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
            slim_tracebacks = [
                [tt.replace("\n", "<br>") for t in e.traceback if (tt := t.strip())]
                for e in self.errors
            ]
            tbs = [
                ("<br>      Traceback:<br>      " if st else "") + "<br>      ".join(st)
                for st in slim_tracebacks
            ]

        def join_parts(parts: Iterable[Tuple[str, str]]):
            last_loc = None
            lines: List[str] = []
            for loc, msg in parts:
                if loc == last_loc:
                    lines.append(f"<br>  {loc} {msg}")
                else:
                    lines.append(f"<br>- {loc} {msg}")

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
    """Summarizes output of all bioimageio validations and tests
    for one specific `ResourceDescr` instance."""

    name: str
    source_name: str
    type: str
    format_version: str
    status: Literal["passed", "failed"]
    details: List[ValidationDetail]
    env: Set[InstalledPackage] = Field(
        default_factory=lambda: {
            InstalledPackage(name="bioimageio.spec", version=VERSION)
        }
    )
    """list of selected, relevant package versions"""

    conda_list: Optional[Sequence[InstalledPackage]] = None
    """parsed output of conda list"""

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

        # fix new lines in table cell
        rows = [[line.replace("\n", "<br>") for line in r] for r in rows]

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
        """Format summary as Markdown string

        Suitable to embed in HTML using '<br>' instead of '\n'.
        """
        info = self._format_md_table(
            [[self.status_icon, f"{self.name.strip('.').strip()} {self.status}"]]
            + ([] if hide_source else [["source", self.source_name]])
            + [
                ["format version", f"{self.type} {self.format_version}"],
            ]
            + ([] if hide_env else [[e.name, e.version] for e in self.env])
        )

        def format_loc(loc: Loc):
            return "`" + (".".join(map(str, root_loc + loc)) or ".") + "`"

        details = [["❓", "location", "detail"]]
        for d in self.details:
            details.append([d.status_icon, format_loc(d.loc), d.name])
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

            if d.recommended_env is not None:
                rec_env = StringIO()
                json_env = d.recommended_env.model_dump(
                    mode="json", exclude_defaults=True
                )
                assert is_yaml_value(json_env)
                write_yaml(json_env, rec_env)
                rec_env_code = rec_env.getvalue().replace("\n", "</code><br><code>")
                details.append(
                    [
                        "🐍",
                        format_loc(d.loc),
                        f"recommended conda env ({d.name})<br>"
                        + f"<pre><code>{rec_env_code}</code></pre>",
                    ]
                )

            if d.conda_compare:
                details.append(
                    [
                        "🐍",
                        format_loc(d.loc),
                        "conda compare ({d.name}):<br>"
                        + d.conda_compare.replace("\n", "<br>"),
                    ]
                )

            for entry in d.errors:
                details.append(
                    [
                        "❌",
                        format_loc(entry.loc),
                        entry.msg.replace("\n\n", "<br>").replace("\n", "<br>"),
                    ]
                )
                if hide_tracebacks:
                    continue

                formatted_tb_lines: List[str] = []
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

                    formatted_tb_lines.append(first_tb_line + tb_rest)

                details.append(["", "", "<br>".join(formatted_tb_lines)])

            for entry in d.warnings:
                details.append(["⚠", format_loc(entry.loc), entry.msg])

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

    @field_validator("env", mode="before")
    def _convert_dict(cls, value: List[Union[List[str], Dict[str, str]]]):
        """convert old env value for backwards compatibility"""
        if isinstance(value, list):
            return [
                (
                    (v["name"], v["version"], v.get("build", ""), v.get("channel", ""))
                    if isinstance(v, dict) and "name" in v and "version" in v
                    else v
                )
                for v in value
            ]
        else:
            return value
