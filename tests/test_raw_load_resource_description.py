from pathlib import Path

import pytest


def test_load_non_existing_rdf():
    from bioimageio.core import load_raw_resource_description

    spec_path = Path("some/none/existing/path/to/spec.model.yaml")

    with pytest.raises(FileNotFoundError):
        load_raw_resource_description(spec_path)


def test_load_raw_model(unet2d_nuclei_broad_any):
    from bioimageio.core import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_nuclei_broad_any)
    assert raw_model
