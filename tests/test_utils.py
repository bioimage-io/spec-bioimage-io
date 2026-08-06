import pytest


def test_license_zenodo():
    """test that all licenses are known or not known by zenodo.
    Run scripts/update_spdx_licenses_zenodo.py to fix this test"""
    from bioimageio.spec.utils import get_spdx_licenses

    for lic in get_spdx_licenses()["licenses"]:
        assert isinstance(lic["isKnownByZenodo"], bool), lic["licenseId"]


def test_load_image_zarr():
    source = "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0062A/6001240.zarr/2"
    from bioimageio.spec.utils import load_image

    img = load_image(source)
    assert img.shape


def test_load_image_zarr_group():
    source = "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0062A/6001240.zarr"

    from bioimageio.spec.utils import load_image

    with pytest.raises(ValueError):
        _ = load_image(source)
