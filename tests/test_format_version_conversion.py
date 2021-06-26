from dataclasses import asdict

from ruamel.yaml import YAML

from bioimageio.spec import schema, maybe_convert_model


yaml = YAML(typ="safe")


def test_model_format_version_conversion(rf_config_path_v0_1, rf_config_path_v0_3):
    rf_model_data_v0_1 = yaml.load(rf_config_path_v0_1)
    rf_model_data = yaml.load(rf_config_path_v0_3)

    expected = asdict(schema.Model().load(rf_model_data))
    converted_data = maybe_convert_model(rf_model_data_v0_1)
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
