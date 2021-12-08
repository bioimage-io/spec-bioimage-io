def test_spec_round_trip(unet2d_nuclei_broad_any_minor):
    from bioimageio.spec import load_raw_resource_description, serialize_raw_resource_description_to_dict

    data = unet2d_nuclei_broad_any_minor
    # monkeypatch: yaml.load already converts timestamp to datetime.datetime, while we serialize it to ISO 8601
    if "timestamp" in data:
        data["timestamp"] = data["timestamp"].isoformat()

    raw_model = load_raw_resource_description(unet2d_nuclei_broad_any_minor)

    serialized = serialize_raw_resource_description_to_dict(raw_model)
    assert isinstance(serialized, dict)
    assert serialized == data

    raw_model_from_serialized = load_raw_resource_description(serialized)
    assert raw_model_from_serialized == raw_model


def test_spec_round_trip_w_attachments(unet2d_nuclei_broad_latest):
    from bioimageio.spec import load_raw_resource_description, serialize_raw_resource_description_to_dict

    data = unet2d_nuclei_broad_latest
    # monkeypatch: yaml.load already converts timestamp to datetime.datetime, while we serialize it to ISO 8601
    if "timestamp" in data:
        data["timestamp"] = data["timestamp"].isoformat()

    data["attachments"] = {"files": ["some_file.ext"], "another_unknown_attachment": ["sub", "whatever", {"weird": 10}]}

    raw_model = load_raw_resource_description(data)

    serialized = serialize_raw_resource_description_to_dict(raw_model)
    assert isinstance(serialized, dict)
    assert serialized == data

    raw_model_from_serialized = load_raw_resource_description(serialized)
    assert raw_model_from_serialized == raw_model
