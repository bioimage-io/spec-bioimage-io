from pathlib import Path

import pytest


def test_load_non_existing_rdf():
    from bioimageio.spec import load_description

    spec_path = Path("some/none/existing/path/to/spec.model.yaml")

    with pytest.raises(FileNotFoundError):
        _ = load_description(spec_path)


def test_load_by_id():
    from bioimageio.spec import InvalidDescr, load_description

    id_ = "frank-water-buffalo"

    model = load_description(id_)
    assert not isinstance(model, InvalidDescr)
    assert model.id == id_
