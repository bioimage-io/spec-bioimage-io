from bioimageio.spec.shared import yaml


def test_v0_1(unet2d_nuclei_broad_v0_1_path):
    from bioimageio.spec.v0_1 import schema

    data = yaml.load(unet2d_nuclei_broad_v0_1_path)
    errors = schema.Model().validate(data)

    assert not errors, errors
