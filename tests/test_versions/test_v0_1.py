from bioimageio.spec.shared import yaml


def test_v0_1(rf_config_path_v0_1):
    from bioimageio.spec.v0_1 import schema

    data = yaml.load(rf_config_path_v0_1)
    errors = schema.Model().validate(data)

    assert not errors, errors
