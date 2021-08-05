from copy import copy
from tempfile import TemporaryFile

from bioimageio.spec.shared import yaml


def test_validate_valid_model(unet2d_nuclei_broad_any):
    from bioimageio.spec.commands import validate

    assert validate(unet2d_nuclei_broad_any, update_format=True, update_format_inner=False) == 0
    assert validate(unet2d_nuclei_broad_any, update_format=False, update_format_inner=False) == 0


def test_validate_invalid_model(unet2d_nuclei_broad_latest):
    from bioimageio.spec.commands import validate
    data = copy(unet2d_nuclei_broad_latest)
    del data["test_inputs"]  # invalidate data
    with TemporaryFile(mode="w+") as f:
        yaml.dump(data, f)
        assert validate(f, update_format=True, update_format_inner=False) == 1
        assert validate(f, update_format=False, update_format_inner=False) == 1
