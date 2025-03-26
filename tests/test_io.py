from pathlib import Path

import pytest

from bioimageio.spec._internal.io import BioimageioYamlContent
from bioimageio.spec._internal.validation_context import ValidationContext


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
        "10.5281/zenodo.11092896",  # backup doi of version 1
        "10.5281/zenodo.11092895",  # concept doi of backup
    ],
)
def test_load_by_id(rid: str):
    from bioimageio.spec._internal.io_utils import open_bioimageio_yaml

    rdf = open_bioimageio_yaml(rid).content
    assert rdf["id"] == "invigorating-lab-coat"


def test_load_description_again(unet2d_data: BioimageioYamlContent):
    from bioimageio.spec import build_description, load_description

    descr = build_description(
        unet2d_data, context=ValidationContext(perform_io_checks=False)
    )
    descr2 = load_description(
        descr,  # pyright: ignore[reportArgumentType]
        perform_io_checks=False,
    )
    assert descr is descr2
