"""check for meaningful validation errors for various invalid input"""
from bioimageio.spec.shared import yaml


def test_list_instead_of_nested_schema(unet2d_nuclei_broad_latest):
    from bioimageio.spec.commands import validate

    assert yaml is not None
    data = yaml.load(unet2d_nuclei_broad_latest)

    # set wrong run_mode (list)
    data["run_mode"] = [{"name": "something"}]

    error = validate(data)["error"]
    assert isinstance(error, dict)
    assert len(error) == 1
    assert error["run_mode"] == ["Expected dictionary, but got list."]


def test_forward_compatibility_error(unet2d_fixed_shape):
    from bioimageio.spec.commands import validate

    assert yaml is not None
    data = yaml.load(unet2d_fixed_shape)

    data["authors"] = 42  # make sure rdf is invalid
    data["format_version"] = "9999.0.0"  # assume it is valid in a future format version

    error = validate(data)["error"]

    # even though the format version is correctly formatted, it should be mentioned here as we treat the future format
    # version as the current latest. If this attempted forward compatibility fails we have to report that we did it.
    assert isinstance(error, dict)
    assert "format_version" in error
