import pytest
from pydantic import HttpUrl

from bioimageio.spec._internal.constants import ALERT
from bioimageio.spec.description import load_description, update_format, validate_format
from bioimageio.spec.types import RawStringMapping, ValidationContext


def test_update_format(stardist04_data: RawStringMapping):
    _ = update_format(stardist04_data)
    with pytest.raises(ValueError):
        _ = update_format(stardist04_data, context={"warning_level": ALERT})


def test_forward_compatibility(unet2d_data: RawStringMapping):
    data = dict(unet2d_data)
    v_future = "9999.0.0"
    data["format_version"] = v_future  # assume it is valid in a future format version

    _, summary = load_description(data, context=ValidationContext(root=HttpUrl("https://example.com/")))
    assert summary.status == "passed", summary

    # expect warning about treating future format version as latest
    ws = summary.warnings
    assert len(ws) == 1, ws
    assert ws[0].loc == ("format_version",), ws[0].loc


def test_no_forward_compatibility(unet2d_data: RawStringMapping):
    data = dict(unet2d_data)
    data["authors"] = 42  # make sure rdf is invalid
    data["format_version"] = "9999.0.0"  # assume it is valid in a future format version

    summary = validate_format(data, context=ValidationContext(root=HttpUrl("https://example.com/")))
    assert summary.status == "failed", summary

    assert len(summary.errors) == 1, summary.errors
    assert summary.errors[0].loc == ("authors",), summary.errors[0].loc

    # expect warning about treating future format version as latest
    ws = summary.warnings
    assert len(ws) == 1, ws
    assert ws[0].loc == ("format_version",), ws[0].loc
