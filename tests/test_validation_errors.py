"""check for meaningful validation errors for various invalid input"""


def test_list_instead_of_nested_schema(unet2d_nuclei_broad_latest):
    from bioimageio.spec.commands import validate

    data = unet2d_nuclei_broad_latest
    # set wrong run_mode (list)
    data["run_mode"] = [{"name": "something"}]

    error = validate(data)["error"]
    print(error)
    assert len(error) == 1
    assert error["run_mode"] == ["Expected dictionary, but got list."]
