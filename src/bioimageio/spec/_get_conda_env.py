from typing import List, Literal, Optional, Union

from typing_extensions import assert_never

from ._internal.gh_utils import set_github_warning
from ._internal.io import FileDescr, get_reader
from ._internal.io_utils import read_yaml
from .conda_env import BioimageioCondaEnv, PipDeps
from .model import v0_4, v0_5
from .model.v0_5 import Version

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

    channels = ["conda-forge", "nodefaults"]

    # dependencies to install pytorch according to
    # https://pytorch.org/get-started/previous-versions/
    v = pytorch_version.base_version
    if v.count(".") == 0:
        v += ".0.0"
    elif v.count(".") == 1:
        v += ".0"

    deps: List[Union[str, PipDeps]] = [f"pytorch=={v}"]
    additional_deps = {
        "1.5.1": "torchvision==0.6.1",
        "1.6.0": "torchvision==0.7.0",
        "1.7.0": "torchvision==0.8.0",
        "1.7.1": "torchvision==0.8.2",
        "1.8.0": "torchvision==0.9.0",
        "1.8.1": "torchvision==0.9.1",
        "1.9.0": "torchvision==0.10.0",
        "1.9.1": "torchvision==0.10.1",
        "1.10.0": "torchvision==0.11.0",
        "1.10.1": "torchvision==0.11.2",
        "1.11.0": "torchvision==0.12.0",
        "1.12.0": "torchvision==0.13.0",
        "1.12.1": "torchvision==0.13.1",
        "1.13.0": "torchvision==0.14.0",
        "1.13.1": "torchvision==0.14.1",
        "2.0.0": "torchvision==0.15.0",
        "2.0.1": "torchvision==0.15.2",
        "2.1.0": "torchvision==0.16.0",
        "2.1.1": "torchvision==0.16.1",
        "2.1.2": "torchvision==0.16.2",
        "2.2.0": "torchvision==0.17.0",
        "2.2.1": "torchvision==0.17.1",
        "2.2.2": "torchvision==0.17.2",
        "2.3.0": "torchvision==0.18.0",
        "2.3.1": "torchvision==0.18.1",
        "2.4.0": "torchvision==0.19.0",
        "2.4.1": "torchvision==0.19.1",
        "2.5.0": "torchvision==0.20.0",
        "2.5.1": "torchvision==0.20.1",
        "2.6.0": "torchvision==0.21.0",
        "2.7.0": "torchvision==0.22.0",
        "2.7.1": "torchvision==0.22.1",
        "2.8.0": "torchvision==0.23.0",
        "2.9.0": "torchvision==0.24.0",
        "2.9.1": "torchvision==0.24.1",
    }.get(v)
    if additional_deps is None:
        set_github_warning(
            "UPDATE NEEDED",
            f"Leaving torchvision unpinned for pytorch=={v}",
        )
        additional_deps = "torchvision"

    deps.append(additional_deps)

    # avoid `undefined symbol: iJIT_NotifyEvent` from `torch/lib/libtorch_cpu.so`
    # see https://github.com/pytorch/pytorch/issues/123097
    if (
        pytorch_version
        < Version(
            "2.1.0"  # TODO: check if this is the correct cutoff where the fix is not longer needed
        )
    ):
        deps.append("mkl ==2024.0.0")

    if pytorch_version < Version("2.2"):
        # avoid ImportError: cannot import name 'packaging' from 'pkg_resources'
        # see https://github.com/pypa/setuptools/issues/4376#issuecomment-2126162839
        deps.append("setuptools <70.0.0")

    if pytorch_version < Version("2.3"):
        # see https://github.com/pytorch/pytorch/issues/107302
        deps.append("numpy <2")

    return BioimageioCondaEnv(channels=channels, dependencies=deps)


def _get_default_onnx_env(*, opset_version: Optional[int]) -> BioimageioCondaEnv:
    if opset_version is None:
        opset_version = 15

    # note: we should not need to worry about the opset version,
    # see https://github.com/microsoft/onnxruntime/blob/master/docs/Versioning.md
    return BioimageioCondaEnv(dependencies=["onnxruntime"])


def _get_default_tf_env(tensorflow_version: Optional[Version]) -> BioimageioCondaEnv:
    if tensorflow_version is None or tensorflow_version.major < 2:
        tensorflow_version = Version("2.17")

    return BioimageioCondaEnv(
        dependencies=[f"tensorflow =={tensorflow_version}"],
    )


def _get_env_from_deps(
    deps: Union[v0_4.Dependencies, FileDescr],
) -> BioimageioCondaEnv:
    if isinstance(deps, v0_4.Dependencies):
        deps_reader = get_reader(deps.file)
        if deps.manager == "pip":
            pip_deps_str = deps_reader.read_text()
            pip_deps = [d.strip() for d in pip_deps_str.split("\n")]
            if "bioimageio.core" not in pip_deps:
                pip_deps.append("bioimageio.core>=0.9.4")

            return BioimageioCondaEnv(
                dependencies=[PipDeps(pip=pip_deps)],
            )
        elif deps.manager in ("conda", "mamba"):
            return BioimageioCondaEnv.model_validate(read_yaml(deps_reader))
        else:
            raise ValueError(f"Dependency manager {deps.manager} not supported")

    elif isinstance(deps, FileDescr):
        deps_reader = deps.get_reader()
        return BioimageioCondaEnv.model_validate(read_yaml(deps_reader))
    else:
        assert_never(deps)
