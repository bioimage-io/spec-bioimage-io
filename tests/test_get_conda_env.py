from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from bioimageio.spec import get_conda_env
from bioimageio.spec._get_conda_env import (
    SupportedWeightsEntry,
    _get_default_pytorch_env,  # pyright: ignore[reportPrivateUsage]
    _get_env_from_deps,  # pyright: ignore[reportPrivateUsage]
)
from bioimageio.spec._internal.validation_context import ValidationContext
from bioimageio.spec._internal.version_type import Version
from bioimageio.spec.model import v0_4, v0_5
from bioimageio.spec.model.v0_5 import (
    OnnxWeightsDescr,
    PytorchStateDictWeightsDescr,
    TorchscriptWeightsDescr,
)


@pytest.mark.parametrize(
    "descr_class,w",
    [
        (
            PytorchStateDictWeightsDescr,
            {
                "authors": [
                    {
                        "name": "Constantin Pape;@bioimage-io",
                        "affiliation": "EMBL Heidelberg",
                        "orcid": "0000-0001-6562-7187",
                    }
                ],
                "sha256": "e4d3885bccbe41cbf6c1d825f3cd2b707c7021ead5593156007e407a16b27cf2",
                "source": "http://files.ilastik.org/bioimageio_test/unet2d_nuclei_broad_weights.torch",
                "architecture": {
                    "callable": "UNet2d",
                    "source": "unet2d.py",
                    "sha256": "68e34520084afde3b160b8774a863ccf2934169838217ace376d6a244c53422b",
                    "kwargs": {"input_channels": 1, "output_channels": 1},
                },
                "dependencies": {
                    "source": "environment.yaml",
                    "sha256": "129d589d2ec801398719b1a6d1bf20ea36b3632f14ccb56a24700df7d719fd10",
                },
                "pytorch_version": "1.5.1",
            },
        ),
        (
            OnnxWeightsDescr,
            {
                "sha256": "f1f086d5e340f9d4d7001a1b62a2b835f9b87a2fb5452c4fe7d8cc821bdf539c",
                "source": "weights.onnx",
                "opset_version": 12,
                "parent": "pytorch_state_dict",
            },
        ),
        (
            TorchscriptWeightsDescr,
            {
                "sha256": "62fa1c39923bee7d58a192277e0dd58f2da9ee810662addadd0f44a3784d9210",
                "source": "weights.pt",
                "parent": "pytorch_state_dict",
                "pytorch_version": "1.5.1",
            },
        ),
    ],
)
def test_get_conda_env(
    descr_class: PytorchStateDictWeightsDescr
    | OnnxWeightsDescr
    | TorchscriptWeightsDescr,
    w: Mapping[str, Any],
    unet2d_path: Path,
):
    with ValidationContext(perform_io_checks=False, root=unet2d_path.parent):
        w_descr = descr_class.model_validate(w)

    conda_env = get_conda_env(entry=w_descr)

    assert conda_env.channels
    assert conda_env.dependencies


def test_get_default_pytorch_env():
    versions: dict[str, list[str | None]] = {
        "pytorch": [
            "1.5.1",
            "1.6.0",
            "1.7.0",
            "1.7.1",
            "1.8.0",
            "1.8.1",
            "1.9.0",
            "1.9.1",
            "1.10.0",
            "1.10.1",
            "1.11.0",
            "1.12.0",
            "1.12.1",
            "1.13.0",
            "1.13.1",
            "2.0.0",
            "2.0.1",
            "2.1.0",
            "2.1.1",
            "2.1.2",
            "2.2.0",
            "2.2.1",
            "2.2.2",
            "2.3.0",
            "2.3.1",
            "2.4.0",
            "2.4.1",
            "2.5.0",
        ]
    }
    envs = [
        _get_default_pytorch_env(pytorch_version=Version.model_validate(v))
        for v in versions["pytorch"]
    ]
    for p in ["torchvision"]:
        versions[p] = [
            env._get_version_pin(p)  # pyright: ignore[reportPrivateUsage]
            for env in envs
        ]

    def assert_lt(p: str, i: int):
        vs = versions[p]
        a, b = vs[i], vs[i + 1]
        assert a is not None, (vs[i], vs[i + 1])
        assert b is not None, (vs[i], vs[i + 1])
        av = Version(a.strip("="))
        bv = Version(b.strip("="))
        assert av < bv, (vs[i], vs[i + 1])

    for i in range(len(versions["pytorch"]) - 1):
        assert_lt("pytorch", i)
        assert_lt("torchvision", i)


@pytest.mark.parametrize("spec", [v0_4, v0_5], ids=["v0_4", "v0_5"])
@pytest.mark.parametrize(
    "format,fields,expected",
    [
        ("OnnxWeightsDescr", {"opset_version": 15}, "onnxruntime"),
        (
            "PytorchStateDictWeightsDescr",
            {"pytorch_version": "2.3.1"},
            "pytorch==2.3.1",
        ),
        ("TorchscriptWeightsDescr", {"pytorch_version": "2.3.1"}, "pytorch==2.3.1"),
        (
            "TensorflowSavedModelBundleWeightsDescr",
            {"tensorflow_version": "2.16.1"},
            "tensorflow ==2.16.1",
        ),
        (
            "KerasHdf5WeightsDescr",
            {"tensorflow_version": "2.16.1"},
            "tensorflow ==2.16.1",
        ),
    ],
)
def test_default_env_for_weights_formats(
    spec: Any, format: str, fields: dict[str, Any], expected: str
):
    data = {"source": "weights.zip", "sha256": "0" * 64, **fields}
    if format == "PytorchStateDictWeightsDescr":
        data["architecture"] = (
            "torch.nn.Linear"
            if spec is v0_4
            else {"import_from": "torch.nn", "callable": "Linear"}
        )

    with ValidationContext(perform_io_checks=False):
        entry = getattr(spec, format).model_validate(data)

    assert expected in get_conda_env(entry=entry).dependencies


@pytest.mark.parametrize("version", [None, "1.15", "2.16.1"])
def test_tensorflow_version_fallback(version: str | None):
    with ValidationContext(perform_io_checks=False):
        entry = v0_4.KerasHdf5WeightsDescr.model_validate(
            {"source": "weights.h5", "tensorflow_version": version}
        )

    expected = "2.16.1" if version == "2.16.1" else "2.17"
    assert f"tensorflow =={expected}" in get_conda_env(entry=entry).dependencies


def test_onnx_without_opset_version():
    with ValidationContext(perform_io_checks=False):
        entry = v0_4.OnnxWeightsDescr.model_validate({"source": "weights.onnx"})

    assert "onnxruntime" in get_conda_env(entry=entry).dependencies


@pytest.mark.parametrize(
    "backend,version,expected",
    [
        ("tensorflow", "2.16.1", "tensorflow ==2.16.1"),
        ("torch", "2.3.1", "pytorch==2.3.1"),
        ("jax", "0.4.35", "jax==0.4.35"),
    ],
)
def test_keras3_backends(backend: str, version: str, expected: str):
    with ValidationContext(perform_io_checks=False):
        entry = v0_5.KerasV3WeightsDescr.model_validate(
            {
                "source": "weights.keras",
                "sha256": "0" * 64,
                "keras_version": "3.0",
                "backend": (backend, version),
            }
        )

    env = get_conda_env(entry=entry)
    assert expected in env.dependencies
    assert "keras >=3.0, <4" in env.dependencies


@pytest.mark.parametrize(
    "version,pin,torchvision,workarounds",
    [
        (
            None,
            "1.10.1",
            "0.11.2",
            ["mkl ==2024.0.0", "setuptools <70.0.0", "numpy <2"],
        ),
        ("2", "2.0.0", "0.15.0", ["mkl ==2024.0.0", "setuptools <70.0.0", "numpy <2"]),
        ("2.1", "2.1.0", "0.16.0", ["setuptools <70.0.0", "numpy <2"]),
        ("2.2.0", "2.2.0", "0.17.0", ["numpy <2"]),
        ("2.3.0", "2.3.0", "0.18.0", []),
        ("2.9.1+cpu", "2.9.1", "0.24.1", []),
    ],
)
def test_pytorch_version_pins_and_workarounds(
    version: str | None, pin: str, torchvision: str, workarounds: list[str]
):
    env = _get_default_pytorch_env(
        pytorch_version=None if version is None else Version(version)
    )

    assert f"pytorch=={pin}" in env.dependencies
    assert f"torchvision=={torchvision}" in env.dependencies
    for workaround in ("mkl ==2024.0.0", "setuptools <70.0.0", "numpy <2"):
        assert (workaround in env.dependencies) == (workaround in workarounds)


def test_unknown_pytorch_version_warns(monkeypatch: pytest.MonkeyPatch):
    warnings: list[tuple[str, str]] = []

    def record_warning(title: str, message: str):
        warnings.append((title, message))

    monkeypatch.setattr(
        "bioimageio.spec._get_conda_env.set_github_warning",
        record_warning,
    )

    env = _get_default_pytorch_env(pytorch_version=Version("99.0.0"))

    assert "pytorch==99.0.0" in env.dependencies
    assert "torchvision" in env.dependencies
    assert warnings == [
        ("UPDATE NEEDED", "Leaving torchvision unpinned for pytorch==99.0.0")
    ]


@pytest.mark.parametrize("env_name", [None, "custom", "DROP"])
@pytest.mark.parametrize(
    "descr_class,manager",
    [
        (v0_4.PytorchStateDictWeightsDescr, "conda"),
        (v0_4.PytorchStateDictWeightsDescr, "mamba"),
        (v0_4.TorchscriptWeightsDescr, "conda"),
        (v0_4.TorchscriptWeightsDescr, "mamba"),
        (v0_4.TensorflowSavedModelBundleWeightsDescr, "conda"),
        (v0_4.TensorflowSavedModelBundleWeightsDescr, "mamba"),
        (v0_5.PytorchStateDictWeightsDescr, "file_descr"),
        (v0_5.TensorflowSavedModelBundleWeightsDescr, "file_descr"),
    ],
)
def test_custom_dependency_env(
    tmp_path: Path,
    manager: str,
    env_name: str | None,
    descr_class: type[SupportedWeightsEntry],
):
    deps_path = tmp_path / "environment.yaml"
    _ = deps_path.write_text(
        "name: original\nchannels: [custom-channel]\ndependencies: [custom-package==1.2]\n"
    )
    data: dict[str, Any] = {
        "source": "weights.zip",
        "sha256": "0" * 64,
        "dependencies": (
            {"source": deps_path}
            if manager == "file_descr"
            else f"{manager}:{deps_path}"
        ),
    }
    if "Pytorch" in descr_class.__name__ or "Torchscript" in descr_class.__name__:
        data["pytorch_version"] = "2.3.1"
    else:
        data["tensorflow_version"] = "2.16.1"
    if "Pytorch" in descr_class.__name__:
        data["architecture"] = (
            {"import_from": "torch.nn", "callable": "Linear"}
            if manager == "file_descr"
            else "torch.nn.Linear"
        )

    with ValidationContext(perform_io_checks=False):
        entry = descr_class.model_validate(data)

    env = get_conda_env(entry=entry, env_name=env_name)
    assert "custom-package==1.2" in env.dependencies
    assert "custom-channel" in env.channels
    assert env.name == {None: "original", "custom": "custom", "DROP": None}[env_name]


@pytest.mark.parametrize("core_requirement", [None, "bioimageio.core"])
def test_pip_dependency_file(tmp_path: Path, core_requirement: str | None):
    deps_path = tmp_path / "requirements.txt"
    _ = deps_path.write_text("  numpy==1.26.4  \n\n" + (core_requirement or ""))
    with ValidationContext(perform_io_checks=False):
        deps = v0_4.Dependencies(f"pip:{deps_path}")

    env = _get_env_from_deps(deps)

    assert env.get_pip_deps() == sorted(
        ["numpy==1.26.4", core_requirement or "bioimageio.core>=0.9.4"]
    )


def test_unsupported_dependency_manager(tmp_path: Path):
    deps_path = tmp_path / "requirements.txt"
    _ = deps_path.write_text("numpy")
    with ValidationContext(perform_io_checks=False):
        deps = v0_4.Dependencies(f"unsupported:{deps_path}")

    with pytest.raises(
        ValueError, match="Dependency manager unsupported not supported"
    ):
        _ = _get_env_from_deps(deps)
