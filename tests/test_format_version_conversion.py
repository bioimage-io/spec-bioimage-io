from dataclasses import asdict

from ruamel.yaml import YAML

from bioimageio.spec import schema, maybe_update_model


yaml = YAML(typ="safe")


def test_model_format_version_conversion(unet2d_nuclei_broad_v0_1_0_path, unet2d_nuclei_broad_latest_path):
    model_data_v0_1 = yaml.load(unet2d_nuclei_broad_v0_1_0_path)
    model_data = yaml.load(unet2d_nuclei_broad_latest_path)

    expected = asdict(schema.Model().load(model_data))
    converted_data = maybe_update_model(model_data_v0_1)
    actual = asdict(schema.Model().load(converted_data))

    # expect converted description
    for ipt in expected["inputs"]:
        ipt["description"] = ipt["name"]

    for out in expected["outputs"]:
        out["description"] = out["name"]

    for key, item in expected.items():
        assert key in actual, key
        assert actual[key] == item, key

    for key, item in actual.items():
        assert key in expected
        assert item == expected[key]
