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


def test_load_dataset_description(covid_if_dataset_path: Path, tmp_path: Path):
    from bioimageio.spec import load_dataset_description
    from bioimageio.spec._io import save_bioimageio_yaml_only
    from bioimageio.spec.dataset.v0_2 import DatasetDescr

    dataset_descr = load_dataset_description(covid_if_dataset_path)
    assert isinstance(dataset_descr, DatasetDescr)

    # this example happens to consist only of the bioimageio.yaml file,
    # so we can test the roundtrip with `save_bioimageio_yaml_only`
    save_bioimageio_yaml_only(dataset_descr, tmp_path / "dataset.yaml")
    dataset_descr2 = load_dataset_description(tmp_path / "dataset.yaml")
    assert isinstance(dataset_descr2, DatasetDescr)  # we cannot expect
    assert dataset_descr.model_dump() == dataset_descr2.model_dump()
