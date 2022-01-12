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


def test_dataset_rdf_round_trip():
    from bioimageio.spec import load_raw_resource_description, serialize_raw_resource_description_to_dict

    data = dict(
        id="platynereis_em_training_data",
        authors=[{"name": "Constantin Pape"}],
        cite=[{"doi": "https://doi.org/10.1016/j.cell.2021.07.017", "text": "Vergara, Pape, Meechan et al."}],
        covers=["https://raw.githubusercontent.com/ilastik/bioimage-io-models/main/dataset_src/platy-cover0.png"],
        description="Training data for EM segmentation of cellular membranes, nuclei, cuticle and cilia in Platynereis.",
        documentation="https://raw.githubusercontent.com/ilastik/bioimage-io-models/main/dataset_src/platy.md",
        format_version="0.2.1",
        license="CC-BY-4.0",
        name="Platynereis EM Traning Data",
        source="https://doi.org/10.5281/zenodo.3675220",
        tags=["electron-microscopy", "platynereis", "cells", "cilia", "nuclei", "instance-segmentation", "3D"],
        type="dataset",
    )
    raw = load_raw_resource_description(data)
    serialized = serialize_raw_resource_description_to_dict(raw)
    # remove keys that are ignored
    data.pop("source")
    assert data == serialized
