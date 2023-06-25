import pathlib

from bioimageio.spec.model import raw_nodes
from bioimageio.spec import collection
from bioimageio.spec.shared import yaml


def test_load_raw_model(unet2d_nuclei_broad_any):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_nuclei_broad_any)
    assert raw_model


def test_load_upsample_raw_model(upsamle_model_rdf):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(upsamle_model_rdf)
    assert raw_model


def test_loaded_remote_raw_model_is_valid(unet2d_nuclei_broad_url):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_nuclei_broad_url)
    raw_model = load_raw_resource_description(raw_model)
    assert raw_model


def test_load_raw_model_fixed_shape(unet2d_fixed_shape):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_fixed_shape)
    assert raw_model


def test_load_raw_model_diff_output_shape(unet2d_diff_output_shape):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_diff_output_shape)
    assert raw_model


def test_load_raw_model_multi_tensor(unet2d_multi_tensor):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_multi_tensor)
    assert raw_model


def test_load_raw_model_expanded_output_shape(unet2d_expanded_output_shape):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_expanded_output_shape)
    assert raw_model


def test_load_raw_model_hpa(hpa_model):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(hpa_model)
    assert raw_model


def test_load_raw_model_stardist(stardist_model):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(stardist_model)
    assert raw_model


def test_load_raw_model_unet2d_keras_tf(unet2d_keras_tf):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_keras_tf, update_to_format="latest")
    assert isinstance(raw_model, raw_nodes.Model)
    # test attachments
    assert len(raw_model.attachments.files) == 1
    attachment = raw_model.attachments.files[0]
    assert isinstance(attachment, pathlib.Path)
    assert (raw_model.root_path / attachment).exists()


def test_load_raw_model_unet2d_keras_tf2(unet2d_keras_tf2):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_keras_tf2, update_to_format="latest")
    assert isinstance(raw_model, raw_nodes.Model)
    # test attachments
    assert len(raw_model.attachments.files) == 3
    attachments = raw_model.attachments.files
    assert all(isinstance(at, pathlib.Path) and (raw_model.root_path / at).exists() for at in attachments)


def test_load_raw_model_to_format(unet2d_nuclei_broad_before_latest):
    from bioimageio.spec import load_raw_resource_description

    assert yaml is not None
    data = yaml.load(unet2d_nuclei_broad_before_latest)
    data["root_path"] = unet2d_nuclei_broad_before_latest.parent
    format_targets = [(0, 3), (0, 4)]
    format_version = tuple(map(int, data["format_version"].split(".")[:2]))

    for target in format_targets:
        if format_version <= target:
            to_format = ".".join(map(str, target))
            raw_model = load_raw_resource_description(data, update_to_format=to_format)
            assert raw_model.format_version[: raw_model.format_version.rfind(".")] == to_format


def test_load_raw_model_converts_invalid_name(unet2d_nuclei_broad_base_path):
    from bioimageio.spec.model.raw_nodes import Model
    from bioimageio.spec import load_raw_resource_description

    assert yaml is not None
    model_dict = yaml.load(unet2d_nuclei_broad_base_path / "rdf_v0_4_0.yaml")
    model_dict["root_path"] = unet2d_nuclei_broad_base_path
    model_dict["name"] = "invalid/name"
    model = load_raw_resource_description(model_dict)
    assert isinstance(model, Model)
    assert model.name == "invalidname"


def test_collection_with_relative_path_in_rdf_source_of_an_entry(partner_collection):
    from bioimageio.spec import load_raw_resource_description
    from bioimageio.spec.collection.utils import resolve_collection_entries
    from bioimageio.spec.dataset.v0_2.raw_nodes import Dataset

    coll = load_raw_resource_description(partner_collection)
    assert isinstance(coll, collection.raw_nodes.Collection)
    resolved_entries = resolve_collection_entries(coll)
    for entry_rdf, entry_error in resolved_entries:
        assert isinstance(entry_rdf, Dataset)
        assert isinstance(entry_rdf.documentation, pathlib.Path) and entry_rdf.documentation.as_posix().endswith(
            "example_specs/collections/partner_collection/datasets/dummy-dataset/README.md"
        )
