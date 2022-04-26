from bioimageio.spec import load_raw_resource_description, serialize_raw_resource_description_to_dict


def test_validate(unet2d_nuclei_broad_collection):
    from bioimageio.spec.commands import validate

    assert not validate(unet2d_nuclei_broad_collection, update_format=True, update_format_inner=False)["error"]
    assert not validate(unet2d_nuclei_broad_collection, update_format=False, update_format_inner=False)["error"]


def test_validate_invalid(unet2d_nuclei_broad_collection):
    from bioimageio.spec.commands import validate

    raw_rd = load_raw_resource_description(unet2d_nuclei_broad_collection)
    data = serialize_raw_resource_description_to_dict(raw_rd, convert_absolute_paths=False)

    data["collection"][0]["name"] = 1  # invalidate data
    assert validate(data, update_format=True, update_format_inner=False)["error"]
    assert validate(data, update_format=False, update_format_inner=False)["error"]
