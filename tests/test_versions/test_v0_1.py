from bioimageio.spec.shared import yaml


def test_v0_1(unet2d_pytorch_model_v01):
    from bioimageio.spec.v0_1 import schema

    data = yaml.load(unet2d_pytorch_model_v01)
    errors = schema.Model().validate(data)

    assert not errors, errors
