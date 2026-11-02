from __future__ import annotations

import subprocess
from io import StringIO
from pathlib import Path
from subprocess import CompletedProcess
from typing import Literal
from unittest.mock import Mock, patch

import pytest
from rich.console import Console

from bioimageio.spec import summary as summary_module
from bioimageio.spec._internal.version_type import Version
from bioimageio.spec.conda_env import CondaEnv
from bioimageio.spec.summary import (
    ErrorEntry,
    InstalledPackage,
    Loc,
    ValidationDetail,
    ValidationSummary,
    WarningEntry,
    format_loc,
)


@pytest.fixture
def summary() -> ValidationSummary:
    return ValidationSummary(
        type="model",
        format_version="0.5.5",
        name="Validation report",
        source_name="model <source>",
        id="test-model",
        version=Version("1.2.3"),
        status="passed",
        details=[],
        saved_conda_list="python 3.13",
    )


def test_save_markdown(tmp_path: Path):
    from bioimageio.spec.summary import ValidationDetail, ValidationSummary

    summary = ValidationSummary(
        type="model",
        format_version="0.5.5",
        name="test",
        source_name="source",
        status="passed",
        details=[ValidationDetail(name="test", status="passed")],
    )
    p = tmp_path / "out.md"
    summary.save_markdown(p)
    assert p.exists()


def test_summary_io(tmp_path: Path):
    from bioimageio.spec.summary import ValidationDetail, ValidationSummary

    summary = ValidationSummary(
        type="generic",
        format_version="0.3.0",
        name="test",
        source_name="source",
        status="failed",
        details=[ValidationDetail(name="test", status="passed")],
    )
    p = tmp_path / "summary.json"
    _ = summary.save(p)
    loaded_summary = summary.load_json(p)
    assert loaded_summary == summary


@pytest.mark.parametrize(
    "loc,plain",
    [
        ((), ""),
        (
            ("weights", "PytorchStateDictWeightsDescr", "source", 0),
            "weights.(PytorchStateDictWeightsDescr).source.0",
        ),
        (("weights", "source", "function-after[validate_url_ok()]"), "weights.source"),
    ],
)
@pytest.mark.parametrize("target", ["md", "html", "plain", "console"])
def test_format_loc(loc: Loc, plain: str, target: str):
    if target == "console":
        formatted = format_loc(loc, Console(file=StringIO()))
    else:
        assert target in ("md", "html", "plain")
        formatted = format_loc(loc, target)
    start, end = {
        "md": ("`", "`"),
        "console": ("`", "`"),
        "html": ("<code>", "</code>"),
        "plain": ("", ""),
    }[target]
    assert formatted == (f"{start}{plain}{end}" if plain else "")


@pytest.mark.parametrize(
    "severity,name", [(20, "info"), (30, "warning"), (35, "alert")]
)
def test_warning_severity_name(severity: Literal[20, 30, 35], name: str):
    assert (
        WarningEntry(
            loc=(), msg="warning", type="test", severity=severity
        ).severity_name
        == name
    )


@pytest.mark.parametrize(
    "status,icon", [("passed", "✔️"), ("valid-format", "🟡"), ("failed", "❌")]
)
def test_status_icons(
    summary: ValidationSummary,
    status: Literal["passed", "valid-format", "failed"],
    icon: str,
):
    summary.status = status
    assert summary.status_icon == icon
    if status != "valid-format":
        assert ValidationDetail(name="test", status=status).status_icon == icon


@pytest.mark.parametrize("status", ["passed", "valid-format", "failed"])
@pytest.mark.parametrize("detail_status", ["passed", "failed"])
@pytest.mark.parametrize("update_status", [True, False])
def test_add_detail(
    summary: ValidationSummary,
    status: Literal["passed", "valid-format", "failed"],
    detail_status: Literal["passed", "failed"],
    update_status: bool,
):
    summary.status = status
    detail = ValidationDetail(name="test", status=detail_status)
    summary.add_detail(detail, update_status=update_status)
    expected = (
        "valid-format"
        if update_status and status == "passed" and detail_status == "failed"
        else status
    )
    assert summary.status == expected
    summary.add_detail(detail)
    assert summary.details == [detail]
    assert summary.status == expected


def test_collect_errors_and_warnings(summary: ValidationSummary):
    errors = [ErrorEntry(loc=(i,), msg=f"error {i}", type="test") for i in range(2)]
    warnings = [
        WarningEntry(loc=(i,), msg=f"warning {i}", type="test") for i in range(2)
    ]
    summary.details = [
        ValidationDetail(
            name=str(i), status="failed", errors=[errors[i]], warnings=[warnings[i]]
        )
        for i in range(2)
    ]
    assert summary.errors == errors
    assert summary.warnings == warnings


@pytest.mark.parametrize(
    "output,expected",
    [
        ("installed packages", "installed packages"),
        ("", "`conda list` exited with 1"),
        (
            FileNotFoundError("missing conda"),
            "Failed to run `conda list`: missing conda",
        ),
    ],
)
def test_conda_list_is_cached(
    summary: ValidationSummary,
    monkeypatch: pytest.MonkeyPatch,
    output: str | Exception,
    expected: str,
):
    summary.saved_conda_list = None
    run = Mock(
        return_value=CompletedProcess(["conda", "list"], 1, stdout=output),
        side_effect=output if isinstance(output, Exception) else None,
    )
    monkeypatch.setattr(subprocess, "run", run)
    assert summary.conda_list == expected
    assert summary.model_dump()["saved_conda_list"] == expected
    run.assert_called_once_with(
        [summary_module.CONDA_CMD, "list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "output,expected",
    [
        ("dependencies match", "dependencies match"),
        ("", "`conda compare` exited with 1"),
        (
            FileNotFoundError("missing conda"),
            "Failed to run `conda compare`: missing conda",
        ),
    ],
)
def test_conda_compare_is_cached(
    monkeypatch: pytest.MonkeyPatch, output: str | Exception, expected: str
):
    detail = ValidationDetail(
        name="test",
        status="passed",
        recommended_env=CondaEnv(dependencies=["python=3.13"]),
    )

    def run(command: list[str], **kwargs: object) -> CompletedProcess[str]:
        assert command[:2] == [summary_module.CONDA_CMD, "compare"]
        assert "python=3.13" in Path(command[2]).read_text(encoding="utf-8")
        if isinstance(output, Exception):
            raise output
        return CompletedProcess(command, 1, stdout=output)

    mock_run = Mock(side_effect=run)
    monkeypatch.setattr(subprocess, "run", mock_run)
    assert detail.conda_compare == expected
    assert detail.model_dump()["saved_conda_compare"] == expected
    mock_run.assert_called_once()
    assert not Path(mock_run.call_args.args[0][2]).exists()


def test_conda_compare_without_environment(monkeypatch: pytest.MonkeyPatch):
    run = Mock()
    monkeypatch.setattr(subprocess, "run", run)
    assert ValidationDetail(name="test", status="passed").conda_compare is None
    run.assert_not_called()


def test_conda_compare_invalid_yaml(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(summary_module, "is_yaml_value", Mock(return_value=False))
    detail = ValidationDetail(name="test", status="passed", recommended_env=CondaEnv())
    assert detail.conda_compare == "Failed to dump recommended env to valid yaml"


def test_load_legacy_fields(summary: ValidationSummary):
    detail = ValidationDetail.model_validate(
        {"name": "test", "status": "passed", "conda_compare": "legacy comparison"}
    )
    assert detail.saved_conda_compare == "legacy comparison"
    assert detail.model_extra == {}
    current = ValidationDetail.model_validate(
        {
            "name": "test",
            "status": "passed",
            "conda_compare": "legacy",
            "saved_conda_compare": "current",
        }
    )
    assert current.saved_conda_compare == "current"
    data = summary.model_dump()
    data["env"] = [
        {"name": "python", "version": "3.13"},
        ["numpy", "2.0", "build", "conda-forge"],
    ]
    loaded = ValidationSummary.model_validate(data)
    assert loaded.env == {
        InstalledPackage("python", "3.13"),
        InstalledPackage("numpy", "2.0", "build", "conda-forge"),
    }
    data["env"] = loaded.env
    assert ValidationSummary.model_validate(data).env == loaded.env


@pytest.mark.parametrize("target", ["md", "html"])
def test_format_summary(summary: ValidationSummary, target: str):
    summary.details = [
        ValidationDetail(
            name="Runtime check",
            status="failed",
            loc=("weights",),
            errors=[
                ErrorEntry(
                    loc=("weights", 0), msg="bad weights\ntry again", type="test"
                )
            ],
            warnings=[
                WarningEntry(loc=("name",), msg="short name", type="test", severity=20),
                WarningEntry(
                    loc=("description",), msg="missing description", type="test"
                ),
            ],
            recommended_env=CondaEnv(dependencies=["python=3.13"]),
            saved_conda_compare="dependencies match",
        )
    ]
    text = (
        summary.format_md(include_conda_list=True)
        if target == "md"
        else summary.format_html(include_conda_list=True)
    )
    for expected in (
        "Validation report",
        "model &lt;source&gt;",
        "test-model",
        "1.2.3",
        "model 0.5.5",
        "Runtime check",
        "bad weights",
        "try again",
        "short name",
        "missing description",
        "python=3.13",
        "dependencies match",
        "python 3.13",
    ):
        assert expected in text
    assert "ℹ" in text
    assert "⚠" in text
    assert "<table>" in text if target == "html" else "|" in text
    assert summary.format(width=80) == summary.format_md(width=80)
    assert "python 3.13" not in summary.format_md()


@pytest.mark.parametrize("target", ["md", "html", "console"])
def test_traceback_details_are_deduplicated_and_limited(
    summary: ValidationSummary, target: Literal["md", "html", "console"]
):
    traces = [f"trace {i}\n" * 20 for i in (0, 0, 1, 2, 3)]
    summary.details = [
        ValidationDetail(
            name="test",
            status="failed",
            errors=[
                ErrorEntry(
                    loc=(),
                    msg="error",
                    type="test",
                    traceback_md=trace,
                    traceback_html=trace,
                )
                for trace in traces
            ],
        )
    ]
    console = Console(file=StringIO(), width=100)
    text = summary_module._format_summary(  # pyright: ignore[reportPrivateUsage]
        summary,
        target=console if target == "console" else target,
        include_conda_list=False,
        width=100,
    )
    assert text.count("trace 0") == 20
    assert "Traceback 3" in text
    assert "Traceback 4" not in text
    assert "Left out 1 more details for brevity." in text


def test_capture_and_render_traceback(summary: ValidationSummary):
    try:
        raise ValueError("example failure")
    except ValueError:
        error = ErrorEntry(loc=(), msg="error", type="test", with_traceback=True)
    assert error.traceback_rich is not None
    assert "ValueError: example failure" in error.traceback_md
    assert "example failure" in error.traceback_html
    assert "_traceback_rich" not in error.model_dump()
    summary.details = [ValidationDetail(name="test", status="failed", errors=[error])]
    output = StringIO()
    _ = summary_module._format_summary(  # pyright: ignore[reportPrivateUsage]
        summary,
        target=Console(file=output, width=100),
        include_conda_list=False,
        width=100,
    )
    assert "example failure" in output.getvalue()
    preformatted = ErrorEntry(
        loc=(),
        msg="error",
        type="test",
        with_traceback=True,
        traceback_md="saved traceback",
    )
    assert preformatted.traceback_rich is None
    assert preformatted.traceback_md == "saved traceback"


def test_save_directory_and_roundtrip(summary: ValidationSummary, tmp_path: Path):
    directory = tmp_path / "nested" / "report"
    paths = summary.save(directory)
    assert paths == [
        directory / f"summary.{suffix}" for suffix in ("json", "md", "html")
    ]
    assert summary.load_json(paths[0]) == summary
    assert paths[1].read_text(encoding="utf-8") == summary.format_md()
    assert paths[2].read_text(encoding="utf-8") == summary.format_html()
    assert summary.save([]) == []
    with pytest.raises(ValueError, match="Unknown summary path suffix '.txt'"):
        _ = summary.save(tmp_path / "summary.txt")


@pytest.mark.parametrize("destination", ["display", "file", "both"])
def test_log_destinations(summary: ValidationSummary, tmp_path: Path, destination: str):
    path = tmp_path / "summary.md"
    to: Literal["display"] | Path | list[Literal["display"] | Path] = (
        "display"
        if destination == "display"
        else path
        if destination == "file"
        else ["display", path]
    )
    with patch.object(ValidationSummary, "display") as display:
        paths = summary.log(to)
    assert display.call_count == (destination != "file")
    assert paths == ([] if destination == "display" else [path])
    assert path.exists() == (destination != "display")


@pytest.mark.parametrize("mode", ["notebook", "terminal", "no_ipython"])
def test_display(
    summary: ValidationSummary, capsys: pytest.CaptureFixture[str], mode: str
):
    get_ipython = Mock(return_value=object() if mode == "notebook" else None)
    display_html = Mock()
    with patch.dict(
        "sys.modules",
        {
            "IPython.core.getipython": (
                None if mode == "no_ipython" else Mock(get_ipython=get_ipython)
            ),
            "IPython.display": Mock(display_html=display_html),
        },
    ):
        summary.display(width=80, include_conda_list=True, tab_size=2, soft_wrap=False)

    if mode == "notebook":
        display_html.assert_called_once_with(
            summary.format_html(width=80, include_conda_list=True), raw=True
        )
        assert capsys.readouterr().out == ""
    else:
        display_html.assert_not_called()
        output = capsys.readouterr().out
        assert "Validation report" in output
        assert "python 3.13" in output


def test_hide_optional_report_sections(summary: ValidationSummary):
    summary.details = [
        ValidationDetail(
            name="test",
            status="failed",
            errors=[
                ErrorEntry(
                    loc=(),
                    msg="visible error",
                    type="test",
                    traceback_md="hidden traceback",
                )
            ],
        )
    ]
    text = summary_module._format_summary(  # pyright: ignore[reportPrivateUsage]
        summary,
        hide_source=True,
        hide_env=True,
        hide_tracebacks=True,
        include_conda_list=False,
        width=100,
    )
    assert "visible error" in text
    for hidden in ("hidden traceback", "model &lt;source&gt;", "bioimageio.spec"):
        assert hidden not in text
