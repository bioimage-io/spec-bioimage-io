import html
import os
import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from itertools import chain
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import TextWrapper
from types import MappingProxyType
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

import annotated_types
import markdown
import rich.console
import rich.markdown
import rich.traceback
from loguru import logger
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic_core.core_schema import ErrorType
from typing_extensions import Annotated, Self, assert_never

from ._internal.io import is_yaml_value
from ._internal.io_utils import write_yaml
from ._internal.type_guards import is_dict
from ._internal.validation_context import ValidationContextSummary
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
from ._version import VERSION
from .conda_env import CondaEnv

CONDA_CMD = "conda.bat" if platform.system() == "Windows" else "conda"

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

    with_traceback: bool = False
    traceback_md: str = ""
    traceback_html: str = ""
    # private rich traceback that is not serialized
    _traceback_rich: Optional[rich.traceback.Traceback] = None

    @property
    def traceback_rich(self):
        return self._traceback_rich

    def model_post_init(self, __context: Any):
        if self.with_traceback and not (self.traceback_md or self.traceback_html):
            self._traceback_rich = rich.traceback.Traceback()
            console = rich.console.Console(
                record=True,
                file=open(os.devnull, "wt", encoding="utf-8"),
                color_system="truecolor",
                width=120,
                tab_size=4,
                soft_wrap=True,
            )
            console.print(self._traceback_rich)
            if not self.traceback_md:
                self.traceback_md = console.export_text(clear=False)

            if not self.traceback_html:
                self.traceback_html = console.export_html(clear=False)


class WarningEntry(ValidationEntry):
    """A warning in a `ValidationDetail`"""

    severity: WarningSeverity = WARNING

    @property
    def severity_name(self) -> WarningSeverityName:
        return WARNING_SEVERITY_TO_NAME[self.severity]


def format_loc(
    loc: Loc, target: Union[Literal["md", "html", "plain"], rich.console.Console]
) -> str:
    """helper to format a location tuple **loc**"""
    loc_str = ".".join(f"({x})" if x[0].isupper() else x for x in map(str, loc))

    # additional field validation can make the location information quite convoluted, e.g.
    # `weights.pytorch_state_dict.dependencies.source.function-after[validate_url_ok(), url['http','https']]` Input should be a valid URL, relative URL without a base
    # therefore we remove the `.function-after[validate_url_ok(), url['http','https']]` here
    loc_str, *_ = loc_str.split(".function-after")
    if loc_str:
        if target == "md" or isinstance(target, rich.console.Console):
            start = "`"
            end = "`"
        elif target == "html":
            start = "<code>"
            end = "</code>"
        elif target == "plain":
            start = ""
            end = ""
        else:
            assert_never(target)

        return f"{start}{loc_str}{end}"
    else:
        return ""


class InstalledPackage(NamedTuple):
    name: str
    version: str
    build: str = ""
    channel: str = ""


class ValidationDetail(BaseModel, extra="allow"):
    """a detail in a validation summary"""

    name: str
    status: Literal["passed", "failed"]
    loc: Loc = ()
    """location in the RDF that this detail applies to"""
    errors: List[ErrorEntry] = Field(  # pyright: ignore[reportUnknownVariableType]
        default_factory=list
    )
    warnings: List[WarningEntry] = Field(  # pyright: ignore[reportUnknownVariableType]
        default_factory=list
    )
    context: Optional[ValidationContextSummary] = None

    recommended_env: Optional[CondaEnv] = None
    """recommended conda environemnt for this validation detail"""

    saved_conda_compare: Optional[str] = None
    """output of `conda compare <recommended env>`"""

    @field_serializer("saved_conda_compare")
    def _save_conda_compare(self, value: Optional[str]):
        return self.conda_compare

    @model_validator(mode="before")
    def _load_legacy(cls, data: Any):
        if is_dict(data):
            field_name = "conda_compare"
            if (
                field_name in data
                and (saved_field_name := f"saved_{field_name}") not in data
            ):
                data[saved_field_name] = data.pop(field_name)

        return data

    @property
    def conda_compare(self) -> Optional[str]:
        if self.recommended_env is None:
            return None

        if self.saved_conda_compare is None:
            dumped_env = self.recommended_env.model_dump(mode="json")
            if is_yaml_value(dumped_env):
                with TemporaryDirectory() as d:
                    path = Path(d) / "env.yaml"
                    with path.open("w", encoding="utf-8") as f:
                        write_yaml(dumped_env, f)

                    compare_proc = subprocess.run(
                        [CONDA_CMD, "compare", str(path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        shell=False,
                        text=True,
                    )
                    self.saved_conda_compare = (
                        compare_proc.stdout
                        or f"`conda compare` exited with {compare_proc.returncode}"
                    )
            else:
                self.saved_conda_compare = (
                    "Failed to dump recommended env to valid yaml"
                )

        return self.saved_conda_compare

    @property
    def status_icon(self):
        if self.status == "passed":
            return "✔️"
        else:
            return "❌"


class ValidationSummary(BaseModel, extra="allow"):
    """Summarizes output of all bioimageio validations and tests
    for one specific `ResourceDescr` instance."""

    name: str
    """Name of the validation"""
    source_name: str
    """Source of the validated bioimageio description"""
    id: Optional[str] = None
    """ID of the resource being validated"""
    type: str
    """Type of the resource being validated"""
    format_version: str
    """Format version of the resource being validated"""
    status: Literal["passed", "valid-format", "failed"]
    """overall status of the bioimageio validation"""
    metadata_completeness: Annotated[float, annotated_types.Interval(ge=0, le=1)] = 0.0
    """Estimate of completeness of the metadata in the resource description.

    Note: This completeness estimate may change with subsequent releases
        and should be considered bioimageio.spec version specific.
    """

    details: List[ValidationDetail]
    """List of validation details"""
    env: Set[InstalledPackage] = Field(
        default_factory=lambda: {
            InstalledPackage(
                name="bioimageio.spec",
                version=VERSION,
            )
        }
    )
    """List of selected, relevant package versions"""

    saved_conda_list: Optional[str] = None

    @field_serializer("saved_conda_list")
    def _save_conda_list(self, value: Optional[str]):
        return self.conda_list

    @property
    def conda_list(self):
        if self.saved_conda_list is None:
            p = subprocess.run(
                [CONDA_CMD, "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=False,
                text=True,
            )
            self.saved_conda_list = (
                p.stdout or f"`conda list` exited with {p.returncode}"
            )

        return self.saved_conda_list

    @property
    def status_icon(self):
        if self.status == "passed":
            return "✔️"
        elif self.status == "valid-format":
            return "🟡"
        else:
            return "❌"

    @property
    def errors(self) -> List[ErrorEntry]:
        return list(chain.from_iterable(d.errors for d in self.details))

    @property
    def warnings(self) -> List[WarningEntry]:
        return list(chain.from_iterable(d.warnings for d in self.details))

    def format(
        self,
        *,
        width: Optional[int] = None,
        include_conda_list: bool = False,
    ):
        """Format summary as Markdown string"""
        return self._format(
            width=width, target="md", include_conda_list=include_conda_list
        )

    format_md = format

    def format_html(
        self,
        *,
        width: Optional[int] = None,
        include_conda_list: bool = False,
    ):
        md_with_html = self._format(
            target="html", width=width, include_conda_list=include_conda_list
        )
        return markdown.markdown(
            md_with_html, extensions=["tables", "fenced_code", "nl2br"]
        )

    def display(
        self,
        *,
        width: Optional[int] = None,
        include_conda_list: bool = False,
        tab_size: int = 4,
        soft_wrap: bool = True,
    ) -> None:
        try:  # render as HTML in Jupyter notebook
            from IPython.core.getipython import get_ipython
            from IPython.display import (
                display_html,  # pyright: ignore[reportUnknownVariableType]
            )
        except ImportError:
            pass
        else:
            if get_ipython() is not None:
                _ = display_html(
                    self.format_html(
                        width=width, include_conda_list=include_conda_list
                    ),
                    raw=True,
                )
                return

        # render with rich
        _ = self._format(
            target=rich.console.Console(
                width=width,
                tab_size=tab_size,
                soft_wrap=soft_wrap,
            ),
            width=width,
            include_conda_list=include_conda_list,
        )

    def add_detail(self, detail: ValidationDetail):
        if detail.status == "failed":
            self.status = "failed"
        elif detail.status != "passed":
            assert_never(detail.status)

        self.details.append(detail)

    def log(
        self,
        to: Union[Literal["display"], Path, Sequence[Union[Literal["display"], Path]]],
    ) -> List[Path]:
        """Convenience method to display the validation summary in the terminal and/or
        save it to disk. See `save` for details."""
        if to == "display":
            display = True
            save_to = []
        elif isinstance(to, Path):
            display = False
            save_to = [to]
        else:
            display = "display" in to
            save_to = [p for p in to if p != "display"]

        if display:
            self.display()

        return self.save(save_to)

    def save(
        self, path: Union[Path, Sequence[Path]] = Path("{id}_summary_{now}")
    ) -> List[Path]:
        """Save the validation/test summary in JSON, Markdown or HTML format.

        Returns:
            List of file paths the summary was saved to.

        Notes:
        - Format is chosen based on the suffix: `.json`, `.md`, `.html`.
        - If **path** has no suffix it is assumed to be a direcotry to which a
          `summary.json`, `summary.md` and `summary.html` are saved to.
        """
        if isinstance(path, (str, Path)):
            path = [Path(path)]

        # folder to file paths
        file_paths: List[Path] = []
        for p in path:
            if p.suffix:
                file_paths.append(p)
            else:
                file_paths.extend(
                    [
                        p / "summary.json",
                        p / "summary.md",
                        p / "summary.html",
                    ]
                )

        now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        for p in file_paths:
            p = Path(str(p).format(id=self.id or "bioimageio", now=now))
            if p.suffix == ".json":
                self.save_json(p)
            elif p.suffix == ".md":
                self.save_markdown(p)
            elif p.suffix == ".html":
                self.save_html(p)
            else:
                raise ValueError(f"Unknown summary path suffix '{p.suffix}'")

        return file_paths

    def save_json(
        self, path: Path = Path("summary.json"), *, indent: Optional[int] = 2
    ):
        """Save validation/test summary as JSON file."""
        json_str = self.model_dump_json(indent=indent)
        path.parent.mkdir(exist_ok=True, parents=True)
        _ = path.write_text(json_str, encoding="utf-8")
        logger.info("Saved summary to {}", path.absolute())

    def save_markdown(self, path: Path = Path("summary.md")):
        """Save rendered validation/test summary as Markdown file."""
        formatted = self.format_md()
        path.parent.mkdir(exist_ok=True, parents=True)
        _ = path.write_text(formatted, encoding="utf-8")
        logger.info("Saved Markdown formatted summary to {}", path.absolute())

    def save_html(self, path: Path = Path("summary.html")) -> None:
        """Save rendered validation/test summary as HTML file."""
        path.parent.mkdir(exist_ok=True, parents=True)

        html = self.format_html()
        _ = path.write_text(html, encoding="utf-8")
        logger.info("Saved HTML formatted summary to {}", path.absolute())

    @classmethod
    def load_json(cls, path: Path) -> Self:
        """Load validation/test summary from a suitable JSON file"""
        json_str = Path(path).read_text(encoding="utf-8")
        return cls.model_validate_json(json_str)

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

    def _format(
        self,
        *,
        target: Union[rich.console.Console, Literal["html", "md"]],
        width: Optional[int],
        include_conda_list: bool,
    ):
        return _format_summary(
            self,
            target=target,
            width=width or 100,
            include_conda_list=include_conda_list,
        )


def _format_summary(
    summary: ValidationSummary,
    *,
    hide_tracebacks: bool = False,  # TODO: remove?
    hide_source: bool = False,  # TODO: remove?
    hide_env: bool = False,  # TODO: remove?
    target: Union[rich.console.Console, Literal["html", "md"]] = "md",
    include_conda_list: bool,
    width: int,
) -> str:
    parts: List[str] = []
    format_table = _format_html_table if target == "html" else _format_md_table
    details_below: Dict[str, Union[str, Tuple[str, rich.traceback.Traceback]]] = {}
    left_out_details: int = 0
    left_out_details_header = "Left out details"

    def add_part(part: str):
        parts.append(part)
        if isinstance(target, rich.console.Console):
            target.print(rich.markdown.Markdown(part))

    def add_section(header: str):
        if target == "md" or isinstance(target, rich.console.Console):
            add_part(f"\n### {header}\n")
        elif target == "html":
            parts.append(f'<h3 id="{header_to_tag(header)}">{header}</h3>')
        else:
            assert_never(target)

    def header_to_tag(header: str):
        return (
            header.replace("`", "")
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "-")
            .lower()
        )

    def add_as_details_below(
        title: str, text: Union[str, Tuple[str, rich.traceback.Traceback]]
    ):
        """returns a header and its tag to link to details below"""

        def make_link(header: str):
            tag = header_to_tag(header)
            if target == "md":
                return f"[{header}](#{tag})"
            elif target == "html":
                return f'<a href="#{tag}">{header}</a>'
            elif isinstance(target, rich.console.Console):
                return f"{header} below"
            else:
                assert_never(target)

        for n in range(1, 4):
            header = f"{title} {n}"
            if header in details_below:
                if details_below[header] == text:
                    return make_link(header)
            else:
                details_below[header] = text
                return make_link(header)

        nonlocal left_out_details
        left_out_details += 1
        return make_link(left_out_details_header)

    @dataclass
    class CodeCell:
        text: str

    @dataclass
    class CodeRef:
        text: str

    def format_code(
        code: str,
        lang: str = "",
        title: str = "Details",
        cell_line_limit: int = 15,
        cell_width_limit: int = 120,
    ) -> Union[CodeRef, CodeCell]:
        if not code.strip():
            return CodeCell("")

        if target == "html":
            html_lang = f' lang="{lang}"' if lang else ""
            code = f"<pre{html_lang}>{code}</pre>"
            put_below = (
                code.count("\n") > cell_line_limit
                or max(map(len, code.split("\n"))) > cell_width_limit
            )
        else:
            put_below = True
            code = f"\n```{lang}\n{code}\n```\n"

        if put_below:
            link = add_as_details_below(title, code)
            return CodeRef(f"See {link}.")
        else:
            return CodeCell(code)

    def format_traceback(entry: ErrorEntry):
        if isinstance(target, rich.console.Console):
            if entry.traceback_rich is None:
                return format_code(entry.traceback_md, title="Traceback")
            else:
                link = add_as_details_below(
                    "Traceback", (entry.traceback_md, entry.traceback_rich)
                )
                return CodeRef(f"See {link}.")

        if target == "md":
            return format_code(entry.traceback_md, title="Traceback")
        elif target == "html":
            return format_code(entry.traceback_html, title="Traceback")
        else:
            assert_never(target)

    def format_text(text: str):
        if target == "html":
            return [f"<pre>{text}</pre>"]
        else:
            return text.split("\n")

    def get_info_table():
        info_rows = [
            [summary.status_icon, summary.name.strip(".").strip()],
            ["status", summary.status],
        ]
        if not hide_source:
            info_rows.append(["source", html.escape(summary.source_name)])

        if summary.id is not None:
            info_rows.append(["id", summary.id])

        info_rows.append(["format version", f"{summary.type} {summary.format_version}"])
        if not hide_env:
            info_rows.extend([[e.name, e.version] for e in sorted(summary.env)])

        if include_conda_list:
            info_rows.append(
                ["conda list", format_code(summary.conda_list, title="Conda List").text]
            )
        return format_table(info_rows)

    def get_details_table():
        details = [["", "Location", "Details"]]

        def append_detail(
            status: str, loc: Loc, text: str, code: Union[CodeRef, CodeCell, None]
        ):
            text_lines = format_text(text)
            status_lines = [""] * len(text_lines)
            loc_lines = [""] * len(text_lines)
            status_lines[0] = status
            loc_lines[0] = format_loc(loc, target)
            for s_line, loc_line, text_line in zip(status_lines, loc_lines, text_lines):
                details.append([s_line, loc_line, text_line])

            if code is not None:
                details.append(["", "", code.text])

        for d in summary.details:
            details.append([d.status_icon, format_loc(d.loc, target), d.name])

            for entry in d.errors:
                append_detail(
                    "❌",
                    entry.loc,
                    entry.msg,
                    None if hide_tracebacks else format_traceback(entry),
                )

            for entry in d.warnings:
                append_detail("⚠", entry.loc, entry.msg, None)

            if d.recommended_env is not None:
                rec_env = StringIO()
                json_env = d.recommended_env.model_dump(
                    mode="json", exclude_defaults=True
                )
                assert is_yaml_value(json_env)
                write_yaml(json_env, rec_env)
                append_detail(
                    "",
                    d.loc,
                    f"recommended conda environment ({d.name})",
                    format_code(
                        rec_env.getvalue(),
                        lang="yaml",
                        title="Recommended Conda Environment",
                    ),
                )

            if d.conda_compare:
                wrapped_conda_compare = "\n".join(
                    TextWrapper(width=width - 4).wrap(d.conda_compare)
                )
                append_detail(
                    "",
                    d.loc,
                    f"conda compare ({d.name})",
                    format_code(
                        wrapped_conda_compare,
                        title="Conda Environment Comparison",
                    ),
                )

        return format_table(details)

    add_part(get_info_table())
    add_part(get_details_table())

    for header, text in details_below.items():
        add_section(header)
        if isinstance(text, tuple):
            assert isinstance(target, rich.console.Console)
            text, rich_obj = text
            target.print(rich_obj)
            parts.append(f"{text}\n")
        else:
            add_part(f"{text}\n")

    if left_out_details:
        parts.append(
            f"\n{left_out_details_header}\nLeft out {left_out_details} more details for brevity.\n"
        )

    return "".join(parts)


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


def _format_html_table(rows: List[List[str]]) -> str:
    """format `rows` as HTML table"""

    def get_line(cells: List[str], cell_tag: Literal["th", "td"] = "td"):
        return (
            ["  <tr>"]
            + [f"    <{cell_tag}>{c}</{cell_tag}>" for c in cells]
            + ["  </tr>"]
        )

    table = ["<table>"] + get_line(rows[0], cell_tag="th")
    for r in rows[1:]:
        table.extend(get_line(r))

    table.append("</table>")

    return "\n".join(table)
