from pathlib import Path
from typing import Any, Iterable, Mapping

import pytest

from bioimageio.spec._description import DISCOVER, LATEST
from bioimageio.spec._internal.types import FormatVersionPlaceholder
from tests.conftest import EXAMPLE_SPECS
from tests.utils import ParameterSet, check_bioimageio_yaml


def get_param(descr_path: Path) -> ParameterSet:
    key = descr_path.relative_to(EXAMPLE_SPECS).as_posix()
    return pytest.param(descr_path, key, id=key)


def yield_valid_descr_paths() -> Iterable[ParameterSet]:
    assert EXAMPLE_SPECS.exists()
    for p in EXAMPLE_SPECS.glob("**/*bioimageio.yaml"):
        if p.name.startswith("invalid"):
            continue

        yield get_param(p)


def yield_invalid_descr_paths() -> Iterable[ParameterSet]:
    assert EXAMPLE_SPECS.exists()
    for p in EXAMPLE_SPECS.glob("**/invalid*bioimageio.yaml"):
        yield get_param(p)


EXCLUDE_FIELDS_FROM_ROUNDTRIP = {
    "models/stardist_example_model/v0_4.bioimageio.yaml": {"dependencies"},
    "models/stardist_example_model/wrong_shape_v0_4.bioimageio.yaml": {"dependencies"},
    "models/stardist_example_model/wrong_shape2_v0_4.bioimageio.yaml": {"dependencies"},
    "models/unet2d_diff_output_shape/v0_4.bioimageio.yaml": {
        "dependencies",
        "weights",
    },
    "models/unet2d_multi_tensor/v0_4.bioimageio.yaml": {"dependencies", "weights"},
    "models/unet2d_nuclei_broad/v0_4_0.bioimageio.yaml": {
        "dependencies",
        "weights",
        "version",
    },
    "models/unet2d_nuclei_broad/v0_4_9.bioimageio.yaml": {"version"},
    "models/upsample_test_model/v0_4.bioimageio.yaml": {"dependencies", "weights"},
}


@pytest.mark.parametrize("format_version", [DISCOVER, LATEST])
@pytest.mark.parametrize("descr_path,key", list(yield_valid_descr_paths()))
def test_example_descr_paths(
    descr_path: Path,
    key: str,
    format_version: FormatVersionPlaceholder,
    bioimageio_json_schema: Mapping[Any, Any],
):
    check_bioimageio_yaml(
        descr_path,
        root=descr_path.parent,
        as_latest=format_version == LATEST,
        exclude_fields_from_roundtrip=EXCLUDE_FIELDS_FROM_ROUNDTRIP.get(key, set()),
        bioimageio_json_schema=bioimageio_json_schema,
    )


@pytest.mark.parametrize("descr_path,key", list(yield_invalid_descr_paths()))
def test_invalid_example_descr_paths(
    descr_path: Path, key: str, bioimageio_json_schema: Mapping[Any, Any]
):
    check_bioimageio_yaml(
        descr_path,
        root=descr_path.parent,
        as_latest=False,
        is_invalid=True,
        bioimageio_json_schema=bioimageio_json_schema,
    )
