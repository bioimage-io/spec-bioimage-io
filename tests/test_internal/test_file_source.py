import pytest

from bioimageio.spec._internal.io_basics import FileName


@pytest.mark.parametrize(
    "name",
    [
        "bioimageio.yaml",
        "rdf.yaml",
        "model.yaml",
        "smth.bioimageio.yaml",
        "smth.rdf.yaml",
        "smth.model.yaml",
    ],
)
def test_is_valid_rdf_name(name: FileName):
    from bioimageio.spec._internal.io import is_valid_rdf_name

    assert is_valid_rdf_name(name), name


@pytest.mark.parametrize("name", ["bioimageio.yml", "RDF.yaml", "smth.yaml"])
def test_is_invalid_rdf_name(name: FileName):
    from bioimageio.spec._internal.io import is_valid_rdf_name

    assert not is_valid_rdf_name(name), name
