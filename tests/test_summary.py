from pathlib import Path


def test_save_markdown(tmp_path: Path):
    from bioimageio.spec.summary import ValidationSummary

    summary = ValidationSummary(
        type="model",
        format_version="0.5.4",
        name="test",
        source_name="source",
        status="passed",
        details=[],
    )
    p = tmp_path / "out.md"
    summary.save_markdown(p)
    assert p.exists()


def test_summary_io(tmp_path: Path):
    from bioimageio.spec.summary import ValidationSummary

    summary = ValidationSummary(
        type="generic",
        format_version="0.3.0",
        name="test",
        source_name="source",
        status="failed",
        details=[],
    )
    p = tmp_path / "summary.json"
    summary.save(p)
    loaded_summary = summary.load(p)
    assert loaded_summary == summary
