import shutil
import subprocess
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

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
        "inputs.axes.concatenable",
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


def test_unet2d_diff_output_shape_reference(tmp_path: Path):
    np = pytest.importorskip("numpy")
    pytest.importorskip("torch")
    model_dir = EXAMPLE_DESCRIPTIONS / "models/unet2d_diff_output_shape"
    copied_model = tmp_path / "model"
    _ = shutil.copytree(
        model_dir, copied_model, ignore=shutil.ignore_patterns("__pycache__")
    )
    _ = subprocess.run(
        [sys.executable, str(copied_model / "create_test_output.py")],
        cwd=tmp_path,
        check=True,
    )
    actual = np.load(copied_model / "test_output.npy")
    expected = np.load(model_dir / "test_output.npy")
    assert actual.shape == (1, 1, 128, 128)
    assert actual.dtype == np.float32
    np.testing.assert_allclose(actual, expected, rtol=1e-3, atol=1e-4)


def test_unet2d_multi_tensor_reference(tmp_path: Path):
    np = pytest.importorskip("numpy")
    pytest.importorskip("torch")
    model_dir = EXAMPLE_DESCRIPTIONS / "models/unet2d_multi_tensor"
    copied_model = tmp_path / "model"
    copied_model.mkdir()
    for name in (
        "create_test_output.py",
        "multi_tensor_unet.py",
        "weights.pt",
        "test_input_0.npy",
        "test_input_1.npy",
    ):
        _ = shutil.copy(model_dir / name, copied_model / name)
    _ = subprocess.run(
        [sys.executable, str(copied_model / "create_test_output.py")],
        cwd=tmp_path,
        check=True,
    )
    for i in range(2):
        actual = np.load(copied_model / f"test_output_{i}.npy")
        expected = np.load(model_dir / f"test_output_{i}.npy")
        assert actual.shape == np.load(model_dir / f"test_input_{i}.npy").shape
        assert actual.dtype == np.float32
        np.testing.assert_allclose(actual, expected, rtol=1e-3, atol=1e-5)
