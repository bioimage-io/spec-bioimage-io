from pathlib import Path
from typing import Any, Iterable, Mapping

import pytest

from tests.conftest import EXAMPLE_DESCRIPTIONS
from tests.test_bioimageio_collection import EXCLUDE_FIELDS_FROM_ROUNDTRIP_DEFAULT
from tests.utils import ParameterSet, check_bioimageio_yaml


def get_param(descr_path: Path) -> ParameterSet:
    key = descr_path.relative_to(EXAMPLE_DESCRIPTIONS).as_posix()
    return pytest.param(descr_path, key, id=key)


def yield_valid_descr_paths() -> Iterable[ParameterSet]:
    assert EXAMPLE_DESCRIPTIONS.exists()
    for p in EXAMPLE_DESCRIPTIONS.glob("**/*bioimageio.yaml"):
        if p.name.startswith("invalid"):
            continue

        yield get_param(p)


def yield_invalid_descr_paths() -> Iterable[ParameterSet]:
    assert EXAMPLE_DESCRIPTIONS.exists()
    for p in EXAMPLE_DESCRIPTIONS.glob("**/invalid*bioimageio.yaml"):
        yield get_param(p)


EXCLUDE_FIELDS_FROM_ROUNDTRIP = {
    "models/stardist_example_model/v0_4.bioimageio.yaml": {
        "channel_colors",
        "dependencies",
    },
    "models/stardist_example_model/wrong_shape_v0_4.bioimageio.yaml": {
        "channel_colors",
        "dependencies",
    },
    "models/stardist_example_model/wrong_shape2_v0_4.bioimageio.yaml": {
        "channel_colors",
        "dependencies",
    },
    "models/unet2d_multi_tensor/bioimageio.yaml": {
        "channel_colors",
        "dependencies",
        "weights",
    },
    "models/unet2d_nuclei_broad/v0_4_0.bioimageio.yaml": {
        "channel_colors",
        "dependencies",
        "weights",
        "version",
    },
    "models/unet2d_nuclei_broad/v0_4_9.bioimageio.yaml": {"version", "channel_colors"},
    "models/upsample_test_model/v0_4.bioimageio.yaml": {
        "dependencies",
        "channel_colors",
        "weights",
    },
}


@pytest.mark.parametrize("descr_path,key", list(yield_valid_descr_paths()))
def test_example_descr_paths(
    descr_path: Path,
    key: str,
    bioimageio_json_schema: Mapping[Any, Any],
):
    excl_fields = set(
        EXCLUDE_FIELDS_FROM_ROUNDTRIP.get(key, EXCLUDE_FIELDS_FROM_ROUNDTRIP_DEFAULT)
    )
    excl_fields.update(("inputs.axes.channel_colors", "outputs.axes.channel_colors"))
    check_bioimageio_yaml(
        descr_path,
        root=descr_path.parent,
        as_latest=False,
        exclude_fields_from_roundtrip=excl_fields,
        bioimageio_json_schema=bioimageio_json_schema,
        perform_io_checks=False,
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
        perform_io_checks=False,
    )
