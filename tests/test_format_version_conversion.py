from dataclasses import asdict

from bioimageio.spec.model import schema
from bioimageio.spec.shared import yaml


def test_model_format_version_conversion(unet2d_nuclei_broad_before_latest, unet2d_nuclei_broad_latest):
    from bioimageio.spec.model.converters import maybe_convert

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
