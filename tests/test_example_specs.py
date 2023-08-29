from pathlib import Path
from typing import Iterable

import pytest

from bioimageio.spec._internal.constants import DISCOVER, LATEST
from bioimageio.spec.types import FormatVersionPlaceholder
from tests.conftest import EXAMPLE_SPECS
from tests.utils import ParameterSet, check_rdf


def get_param(rdf: Path) -> ParameterSet:
    rdf_key = rdf.relative_to(EXAMPLE_SPECS).as_posix()
    return pytest.param(rdf, rdf_key, id=rdf_key)


def yield_valid_rdf_paths() -> Iterable[ParameterSet]:
    assert EXAMPLE_SPECS.exists()
    for rdf in EXAMPLE_SPECS.glob("**/*.yaml"):
        if rdf.name.startswith("rdf"):
            yield get_param(rdf)


def yield_invalid_rdf_paths() -> Iterable[ParameterSet]:
    assert EXAMPLE_SPECS.exists()
    for rdf in EXAMPLE_SPECS.glob("**/*.yaml"):
        if rdf.name.startswith("invalid_rdf"):
            yield get_param(rdf)


EXCLUDE_FIELDS_FROM_ROUNDTRIP = {
    "models/stardist_example_model/rdf_v0_4.yaml": {"dependencies"},
    "models/stardist_example_model/rdf_wrong_shape_v0_4.yaml": {"dependencies"},
    "models/stardist_example_model/rdf_wrong_shape2_v0_4.yaml": {"dependencies"},
    "models/unet2d_diff_output_shape/rdf_v0_4.yaml": {
        "dependencies",
        "weights",
    },
    "models/unet2d_multi_tensor/rdf_v0_4.yaml": {"dependencies", "weights"},
    "models/unet2d_multi_tensor/rdf_v0_4.yaml": {"dependencies", "weights"},
    "models/unet2d_nuclei_broad/rdf_v0_4_0.yaml": {
        "dependencies",
        "weights",
    },
    "models/upsample_test_model/rdf_v0_4.yaml": {"dependencies", "weights"},
}


@pytest.mark.parametrize("format_version", [DISCOVER, LATEST])
@pytest.mark.parametrize("rdf_path,rdf_key", list(yield_valid_rdf_paths()))
def test_example_rdfs(rdf_path: Path, rdf_key: str, format_version: FormatVersionPlaceholder):
    check_rdf(
        rdf_path.parent,
        rdf_path,
        as_latest=format_version == LATEST,
        exclude_fields_from_roundtrip=EXCLUDE_FIELDS_FROM_ROUNDTRIP.get(rdf_key, set()),
    )


@pytest.mark.parametrize("rdf_path,rdf_key", list(yield_invalid_rdf_paths()))
def test_invalid_example_rdfs(rdf_path: Path, rdf_key: str):
    check_rdf(rdf_path.parent, rdf_path, as_latest=False, is_invalid=True)
