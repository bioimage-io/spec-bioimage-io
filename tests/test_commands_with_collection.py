from copy import copy


def test_validate(unet2d_nuclei_broad_collection):
    from bioimageio.spec.commands import validate

    assert not validate(unet2d_nuclei_broad_collection, update_format=True, update_format_inner=False)["error"]
    assert not validate(unet2d_nuclei_broad_collection, update_format=False, update_format_inner=False)["error"]


def test_validate_invalid(unet2d_nuclei_broad_collection):
    from bioimageio.spec.commands import validate

    data = copy(unet2d_nuclei_broad_collection)
    data["collection"][0]["name"] = 1  # invalidate data
    assert validate(data, update_format=True, update_format_inner=False)["error"]
    assert validate(data, update_format=False, update_format_inner=False)["error"]
