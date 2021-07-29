from pathlib import Path

import pytest
from marshmallow import ValidationError


def test_load_non_existing_rdf():
    from bioimageio.spec import load_resource_description

    spec_path = Path("some/none/existing/path/to/spec.model.yaml")

    with pytest.raises(FileNotFoundError):
        load_resource_description(spec_path)


def test_load_non_valid_rdf_name():
    from bioimageio.spec import load_resource_description

    spec_path = Path("some/none/existing/path/to/spec.not_valid_suffix")

    with pytest.raises(ValidationError):
        load_resource_description(spec_path)


def test_load_raw_model(unet2d_nuclei_broad_any_path):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_nuclei_broad_any_path)
    assert raw_model


def test_load_raw_model_from_package(unet2d_nuclei_broad_latest_package_path):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_nuclei_broad_latest_package_path)
    assert raw_model


def test_load_model(unet2d_nuclei_broad_any_path):
    from bioimageio.spec import load_resource_description

    model = load_resource_description(unet2d_nuclei_broad_any_path)
    assert model


def test_load_model_from_package(unet2d_nuclei_broad_any_path):
    from bioimageio.spec import load_resource_description

    model = load_resource_description(unet2d_nuclei_broad_any_path)
    assert model
