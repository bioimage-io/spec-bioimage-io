from dataclasses import asdict

from ruamel.yaml import YAML

from bioimageio.spec import schema, maybe_convert_model


yaml = YAML(typ="safe")


def test_model_nodes_format_0_1_to_0_3(unet_pytorch_model_v01, unet_pytorch_model_v032):
    model_data_v0_1 = yaml.load(unet_pytorch_model_v01)
    model_data = yaml.load(unet_pytorch_model_v032)

    expected = asdict(schema.Model().load(model_data))
    converted_data = maybe_convert_model(model_data_v0_1)
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
