def test_invalid_description_get_reason():
    from bioimageio.spec import build_description
    from bioimageio.spec._internal.common_nodes import InvalidDescr

    descr = build_description({"invalid": True, "another_reason": "this bad"})

    assert isinstance(descr, InvalidDescr)
    reason = descr.get_reason()
    assert reason is not None
