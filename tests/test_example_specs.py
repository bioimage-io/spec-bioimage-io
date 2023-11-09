from pathlib import Path
from typing import Iterable

import pytest

from bioimageio.spec._internal.constants import DISCOVER, LATEST
from bioimageio.spec._internal.types import FormatVersionPlaceholder
from tests.conftest import EXAMPLE_SPECS
from tests.utils import ParameterSet, check_bioimageio_yaml


def get_param(rdf: Path) -> ParameterSet:
    key = rdf.relative_to(EXAMPLE_SPECS).as_posix()
    return pytest.param(rdf, key, id=key)


def yield_valid_descr_paths() -> Iterable[ParameterSet]:
    assert EXAMPLE_SPECS.exists()
    for p in EXAMPLE_SPECS.glob("**/*bioimageio.yaml"):
        yield get_param(p)


def yield_invalid_descr_paths() -> Iterable[ParameterSet]:
    assert EXAMPLE_SPECS.exists()
    for p in EXAMPLE_SPECS.glob("**/invalid*bioimageio.yaml"):
        yield get_param(p)


EXCLUDE_FIELDS_FROM_ROUNDTRIP = {
    "models/stardist_example_model/rdf_v0_4.yaml": {"dependencies"},
    "models/stardist_example_model/rdf_wrong_shape_v0_4.yaml": {"dependencies"},
    "models/stardist_example_model/rdf_wrong_shape2_v0_4.yaml": {"dependencies"},
    "models/unet2d_diff_output_shape/rdf_v0_4.yaml": {
        "dependencies",
        "weights",
    },
    "models/unet2d_multi_tensor/rdf_v0_4.yaml": {"dependencies", "weights"},
    "models/unet2d_nuclei_broad/rdf_v0_4_0.yaml": {
        "dependencies",
        "weights",
    },
    "models/upsample_test_model/rdf_v0_4.yaml": {"dependencies", "weights"},
}


@pytest.mark.parametrize("format_version", [DISCOVER, LATEST])
@pytest.mark.parametrize("descr_path,key", list(yield_valid_descr_paths()))
def test_example_rdfs(descr_path: Path, key: str, format_version: FormatVersionPlaceholder):
    check_bioimageio_yaml(
        descr_path,
        root=descr_path.parent,
        as_latest=format_version == LATEST,
        exclude_fields_from_roundtrip=EXCLUDE_FIELDS_FROM_ROUNDTRIP.get(key, set()),
    )


@pytest.mark.parametrize("descr_path,key", list(yield_invalid_descr_paths()))
def test_invalid_example_rdfs(descr_path: Path, key: str):
    check_bioimageio_yaml(descr_path, root=descr_path.parent, as_latest=False, is_invalid=True)
