from dataclasses import asdict
from typing import Tuple

import pytest
from packaging.version import Version

from bioimageio.spec.model import schema
from bioimageio.spec.shared import yaml


def test_model_format_version_conversion(unet2d_nuclei_broad_before_latest, unet2d_nuclei_broad_latest):
    from bioimageio.spec.model.converters import maybe_convert

    assert yaml is not None
    old_model_data = yaml.load(unet2d_nuclei_broad_before_latest)
    model_data = yaml.load(unet2d_nuclei_broad_latest)

    expected = asdict(schema.Model().load(model_data))
    converted_data = maybe_convert(old_model_data)
    actual = asdict(schema.Model().load(converted_data))

    if old_model_data["format_version"] == "0.1.0":
        # expect converted description
        for ipt in expected["inputs"]:
            ipt["description"] = ipt["name"]

        for out in expected["outputs"]:
            out["description"] = out["name"]

    # ignore new optional fields
    if tuple(map(int, old_model_data["format_version"].split("."))) < (0, 4, 0):
        expected.pop("maintainers")
        actual.pop("maintainers")
    if tuple(map(int, old_model_data["format_version"].split("."))) < (0, 4, 4):
        expected.pop("download_url")
        actual.pop("download_url")
        expected.pop("training_data")
        actual.pop("training_data")

    for key, item in expected.items():
        assert key in actual, key
        assert actual[key] == item, key

    for key, item in actual.items():
        assert key in expected
        assert item == expected[key]


# todo: break forward compatibility on major version difference?
@pytest.mark.parametrize("v_diff", [(0, 0, 1), (0, 1, 0), (1, 0, 0), (0, 1, 1)])
def test_forward_compatible(v_diff: Tuple[int, int, int], unet2d_nuclei_broad_latest):
    from bioimageio.spec import load_raw_resource_description
    from bioimageio.spec.model import format_version

    fv_key = "format_version"

    assert yaml is not None
    model_data = yaml.load(unet2d_nuclei_broad_latest)

    v_latest: Version = Version(format_version)
    v_future: str = ".".join(
        [str(latest + diff) for latest, diff in zip([v_latest.major, v_latest.minor, v_latest.micro], v_diff)]
    )

    future_model_data = dict(model_data)
    future_model_data[fv_key] = v_future

    rd = load_raw_resource_description(future_model_data)
    assert rd.format_version == format_version
    assert hasattr(rd, "config")
    assert rd.config["bioimageio"]["original_format_version"] == v_future
