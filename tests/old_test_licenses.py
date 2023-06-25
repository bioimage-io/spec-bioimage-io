from bioimageio.spec.shared import LICENSES


def test_licenses_read_and_reformatted():
    """Make sure LICENSES is dict of dicts"""
    assert isinstance(LICENSES, dict)
    assert all(isinstance(v, dict) for k, v in LICENSES.items())
