from pathlib import Path
from typing import Iterable

import pytest

from tests.conftest import EXAMPLE_SPECS
from tests.utils import check_rdf


def yield_valid_rdf_paths() -> Iterable[Path]:
    assert EXAMPLE_SPECS.exists()
    for rdf in EXAMPLE_SPECS.glob("**/*.yaml"):
        if rdf.name.startswith("rdf"):
            yield rdf


def yield_invalid_rdf_paths() -> Iterable[Path]:
    assert EXAMPLE_SPECS.exists()
    for rdf in EXAMPLE_SPECS.glob("**/*.yaml"):
        if rdf.name.startswith("invalid_rdf"):
            yield rdf


EXCLUDE_FIELDS_FROM_ROUNDTRIP = {
    Path("models/stardist_example_model/rdf_v0_4.yaml"): {"dependencies"},
    Path("models/stardist_example_model/rdf_wrong_shape_v0_4.yaml"): {"dependencies"},
    Path("models/stardist_example_model/rdf_wrong_shape2_v0_4.yaml"): {"dependencies"},
    Path("models/unet2d_diff_output_shape/rdf_v0_4.yaml"): {
        "dependencies",
        "weights",
    },
    Path("models/unet2d_multi_tensor/rdf_v0_4.yaml"): {"dependencies", "weights"},
    Path("models/unet2d_multi_tensor/rdf_v0_4.yaml"): {"dependencies", "weights"},
    Path("models/unet2d_nuclei_broad/rdf_v0_4_0.yaml"): {
        "dependencies",
        "weights",
    },
    Path("models/upsample_test_model/rdf_v0_4.yaml"): {"dependencies", "weights"},
}


@pytest.mark.parametrize("rdf_path", list(yield_valid_rdf_paths()))
@pytest.mark.parametrize("as_latest", [False, True])
def test_example_rdfs(rdf_path: Path, as_latest: bool):
    check_rdf(
        rdf_path.parent, rdf_path, as_latest, exclude_fields_from_roundtrip=EXCLUDE_FIELDS_FROM_ROUNDTRIP[rdf_path]
    )


@pytest.mark.parametrize("rdf_path", list(yield_invalid_rdf_paths()))
def test_invalid_example_rdfs(rdf_path: Path, as_latest: bool):
    check_rdf(rdf_path.parent, rdf_path, as_latest=as_latest, is_invalid=True)
