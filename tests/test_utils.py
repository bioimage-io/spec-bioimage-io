def test_license_zenodo():
    """test that all licenses are known or not known by zenodo.
    Run scripts/update_spdx_licenses_zenodo.py to fix this test"""
    from bioimageio.spec.utils import get_spdx_licenses

    for lic in get_spdx_licenses()["licenses"]:
        assert isinstance(lic["isKnownByZenodo"], bool), lic["licenseId"]
