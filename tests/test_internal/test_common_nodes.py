def test_invalid_description_get_reason():
    from bioimageio.spec import validate_format
    from bioimageio.spec._internal.common_nodes import InvalidDescr

    descr = validate_format({"invalid": True, "another_reason": "this bad"})

    assert isinstance(descr, InvalidDescr)
    reason = descr.get_reason()
    assert reason is not None
    assert "this bad" in reason
