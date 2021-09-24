from copy import copy


def test_validate_valid_model(unet2d_nuclei_broad_any):
    from bioimageio.spec.commands import validate

    assert not validate(unet2d_nuclei_broad_any, update_format=True, update_format_inner=False)
    assert not validate(unet2d_nuclei_broad_any, update_format=False, update_format_inner=False)


def test_validate_invalid_model(unet2d_nuclei_broad_latest):
    from bioimageio.spec.commands import validate

    data = copy(unet2d_nuclei_broad_latest)
    del data["test_inputs"]  # invalidate data
    assert validate(data, update_format=True, update_format_inner=False)
    assert validate(data, update_format=False, update_format_inner=False)
