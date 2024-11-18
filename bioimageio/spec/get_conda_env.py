from typing import List, Literal, Optional, Union

from typing_extensions import assert_never

from ._internal.gh_utils import set_github_warning
from ._internal.io_utils import ZipPath, read_yaml
from .common import RelativeFilePath
from .conda_env import BioimageioCondaEnv, PipDeps
from .model import v0_4, v0_5
from .model.v0_5 import Version
from .utils import download

SupportedWeightsEntry = Union[
    v0_4.KerasHdf5WeightsDescr,
    v0_4.OnnxWeightsDescr,
    v0_4.PytorchStateDictWeightsDescr,
    v0_4.TensorflowSavedModelBundleWeightsDescr,
    v0_4.TorchscriptWeightsDescr,
    v0_5.KerasHdf5WeightsDescr,
    v0_5.OnnxWeightsDescr,
    v0_5.PytorchStateDictWeightsDescr,
    v0_5.TensorflowSavedModelBundleWeightsDescr,
    v0_5.TorchscriptWeightsDescr,
]


def get_conda_env(
    *,
    entry: SupportedWeightsEntry,
    env_name: Optional[Union[Literal["DROP"], str]] = None,
) -> BioimageioCondaEnv:
    """get the recommended Conda environment for a given weights entry description"""
    if isinstance(entry, (v0_4.OnnxWeightsDescr, v0_5.OnnxWeightsDescr)):
        conda_env = _get_default_onnx_env(opset_version=entry.opset_version)
    elif isinstance(
        entry,
        (
            v0_4.PytorchStateDictWeightsDescr,
            v0_5.PytorchStateDictWeightsDescr,
            v0_4.TorchscriptWeightsDescr,
            v0_5.TorchscriptWeightsDescr,
        ),
    ):
        if (
            isinstance(entry, v0_5.TorchscriptWeightsDescr)
            or entry.dependencies is None
        ):
            conda_env = _get_default_pytorch_env(pytorch_version=entry.pytorch_version)
        else:
            conda_env = _get_env_from_deps(entry.dependencies)

    elif isinstance(
        entry,
        (
            v0_4.TensorflowSavedModelBundleWeightsDescr,
            v0_5.TensorflowSavedModelBundleWeightsDescr,
        ),
    ):
        if entry.dependencies is None:
            conda_env = _get_default_tf_env(tensorflow_version=entry.tensorflow_version)
        else:
            conda_env = _get_env_from_deps(entry.dependencies)
    elif isinstance(
        entry,
        (v0_4.KerasHdf5WeightsDescr, v0_5.KerasHdf5WeightsDescr),
    ):
        conda_env = _get_default_tf_env(tensorflow_version=entry.tensorflow_version)
    else:
        assert_never(entry)

    if env_name == "DROP":
        conda_env.name = None
    elif env_name is not None:
        conda_env.name = env_name

    return conda_env


def _get_default_pytorch_env(
    *,
    pytorch_version: Optional[Version] = None,
) -> BioimageioCondaEnv:
    if pytorch_version is None:
        pytorch_version = Version("1.10.1")

    # dependencies to install pytorch according to https://pytorch.org/get-started/previous-versions/
    if (v := str(pytorch_version)) == "1.6.0":
        deps: List[Union[str, PipDeps]] = [f"pytorch=={v}", "torchvision==0.7.0"]
    elif v == "1.7.0":
        deps = [f"pytorch=={v}", "torchvision==0.8.0", "torchaudio==0.7.0"]
    elif v == "1.7.1":
        deps = [f"pytorch=={v}", "torchvision==0.8.2", "torchaudio==0.7.1"]
    elif v == "1.8.0":
        deps = [f"pytorch=={v}", "torchvision==0.9.0", "torchaudio==0.8.0"]
    elif v == "1.8.1":
        deps = [f"pytorch=={v}", "torchvision==0.9.1", "torchaudio==0.8.1"]
    elif v == "1.9.0":
        deps = [f"pytorch=={v}", "torchvision==0.10.0", "torchaudio==0.9.0"]
    elif v == "1.9.1":
        deps = [f"pytorch=={v}", "torchvision==0.10.1", "torchaudio==0.9.1"]
    elif v == "1.10.0":
        deps = [f"pytorch=={v}", "torchvision==0.11.0", "torchaudio==0.10.0"]
    elif v == "1.10.1":
        deps = [f"pytorch=={v}", "torchvision==0.11.2", "torchaudio==0.10.1"]
    elif v == "1.11.0":
        deps = [f"pytorch=={v}", "torchvision==0.12.0", "torchaudio==0.11.0"]
    elif v == "1.12.0":
        deps = [f"pytorch=={v}", "torchvision==0.13.0", "torchaudio==0.12.0"]
    elif v == "1.12.1":
        deps = [f"pytorch=={v}", "torchvision==0.13.1", "torchaudio==0.12.1"]
    elif v == "1.13.0":
        deps = [f"pytorch=={v}", "torchvision==0.14.0", "torchaudio==0.13.0"]
    elif v == "1.13.1":
        deps = [f"pytorch=={v}", "torchvision==0.14.1", "torchaudio==0.13.1"]
    elif v == "2.0.0":
        deps = [f"pytorch=={v}", "torchvision==0.15.0", "torchaudio==2.0.0"]
    elif v == "2.0.1":
        deps = [f"pytorch=={v}", "torchvision==0.15.2", "torchaudio==2.0.2"]
    elif v == "2.1.0":
        deps = [f"pytorch=={v}", "torchvision==0.16.0", "torchaudio==2.1.0"]
    elif v == "2.1.1":
        deps = [f"pytorch=={v}", "torchvision==0.16.1", "torchaudio==2.1.1"]
    elif v == "2.1.2":
        deps = [f"pytorch=={v}", "torchvision==0.16.2", "torchaudio==2.1.2"]
    elif v == "2.2.0":
        deps = [f"pytorch=={v}", "torchvision==0.17.0", "torchaudio==2.2.0"]
    elif v == "2.2.1":
        deps = [f"pytorch=={v}", "torchvision==0.17.1", "torchaudio==2.2.1"]
    elif v == "2.2.2":
        deps = [f"pytorch=={v}", "torchvision==0.17.2", "torchaudio==2.2.2"]
    elif v == "2.3.0":
        deps = [f"pytorch=={v}", "torchvision==0.18.0", "torchaudio==2.3.0"]
    elif v == "2.3.1":
        deps = [f"pytorch=={v}", "torchvision==0.18.1", "torchaudio==2.3.1"]
    elif v == "2.4.0":
        deps = [f"pytorch=={v}", "torchvision==0.19.0", "torchaudio==2.4.0"]
    elif v == "2.4.1":
        deps = [f"pytorch=={v}", "torchvision==0.19.1", "torchaudio==2.4.1"]
    elif v == "2.5.0":
        deps = [f"pytorch=={v}", "torchvision==0.20.0", "torchaudio==2.5.0"]
    else:
        set_github_warning(
            "UPDATE NEEDED", f"Specify pins for additional pytorch=={v} dependencies!"
        )
        deps = [f"pytorch=={v}", "torchvision", "torchaudio"]

    deps.append("cpuonly")

    # avoid `undefined symbol: iJIT_NotifyEvent` from `torch/lib/libtorch_cpu.so`
    # see https://github.com/pytorch/pytorch/issues/123097
    if pytorch_version < Version(
        "2.1.0"  # TODO: check if this is the correct cutoff where the fix is not longer needed
    ):
        deps.append("mkl ==2024.0.0")

    if pytorch_version.major == 1 or (
        pytorch_version.major == 2 and pytorch_version.minor < 2
    ):
        # avoid ImportError: cannot import name 'packaging' from 'pkg_resources'
        # see https://github.com/pypa/setuptools/issues/4376#issuecomment-2126162839
        deps.append("setuptools <70.0.0")

    if pytorch_version < Version(
        "2.3"
    ):  # TODO: verify that future pytorch 2.4 is numpy 2.0 compatible
        # make sure we have a compatible numpy version
        # see https://github.com/pytorch/vision/issues/8460
        deps.append("numpy <2")
    else:
        deps.append("numpy >=2,<3")

    return BioimageioCondaEnv(
        channels=["pytorch", "conda-forge", "nodefaults"],
        dependencies=deps,
    )


def _get_default_onnx_env(*, opset_version: Optional[int]) -> BioimageioCondaEnv:
    if opset_version is None:
        opset_version = 15

    # note: we should not need to worry about the opset version,
    # see https://github.com/microsoft/onnxruntime/blob/master/docs/Versioning.md
    return BioimageioCondaEnv(dependencies=["onnxruntime"])


def _get_default_tf_env(tensorflow_version: Optional[Version]) -> BioimageioCondaEnv:
    if tensorflow_version is None:
        tensorflow_version = Version("1.15")

    # tensorflow 1 is not available on conda, so we need to inject this as a pip dependency
    if tensorflow_version.major == 1:
        tensorflow_version = max(
            tensorflow_version, Version("1.13")
        )  # tf <1.13 not available anymore
        deps = (
            "pip",
            "python=3.7.*",  # tf 1.15 not available for py>=3.8
            PipDeps(
                pip=[
                    "bioimageio.core",  # get bioimageio.core (and its dependencies) via pip as well to avoid conda/pip mix
                    f"tensorflow =={tensorflow_version}",
                    "protobuf <4.0",  # protobuf pin: tf 1 does not pin an upper limit for protobuf, but fails to load models saved with protobuf 3 when installing protobuf 4.
                ]
            ),
        )
        return BioimageioCondaEnv(
            dependencies=list(deps),
        )
    else:
        return BioimageioCondaEnv(
            dependencies=["bioimageio.core", f"tensorflow =={tensorflow_version}"],
        )


def _get_env_from_deps(
    deps: Union[v0_4.Dependencies, v0_5.EnvironmentFileDescr],
) -> BioimageioCondaEnv:
    if isinstance(deps, v0_4.Dependencies):
        if deps.manager == "pip":
            pip_deps_str = download(deps.file).path.read_text(encoding="utf-8")
            assert isinstance(pip_deps_str, str)
            pip_deps = [d.strip() for d in pip_deps_str.split("\n")]
            if "bioimageio.core" not in pip_deps:
                pip_deps.append("bioimageio.core")

            return BioimageioCondaEnv(
                dependencies=[PipDeps(pip=pip_deps)],
            )
        elif deps.manager not in ("conda", "mamba"):
            raise ValueError(f"Dependency manager {deps.manager} not supported")
        else:
            deps_source = (
                deps.file.absolute()
                if isinstance(deps.file, RelativeFilePath)
                else deps.file
            )
            if isinstance(deps_source, ZipPath):
                local = deps_source
            else:
                local = download(deps_source).path

            return BioimageioCondaEnv.model_validate(read_yaml(local))
    elif isinstance(deps, v0_5.EnvironmentFileDescr):
        local = download(deps.source).path
        return BioimageioCondaEnv.model_validate(read_yaml(local))
    else:
        assert_never(deps)
