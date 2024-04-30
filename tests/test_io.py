from pathlib import Path

import pytest


def test_load_non_existing_rdf():
    from bioimageio.spec import load_description

    spec_path = Path("some/none/existing/path/to/spec.model.yaml")

    with pytest.raises(FileNotFoundError):
        _ = load_description(spec_path)


@pytest.mark.parametrize(
    "rid",
    [
        "invigorating-lab-coat",
        "invigorating-lab-coat/1",
        "invigorating-lab-coat/staged/1",
    ],
)
def test_load_by_id(rid: str):
    from bioimageio.spec import InvalidDescr, load_description

    model = load_description(rid)
    assert not isinstance(model, InvalidDescr)
    assert model.id == rid.split("/")[0]
