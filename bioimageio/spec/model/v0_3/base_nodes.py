import distutils.version
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Tuple, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.rdf import v0_2 as rdf
from bioimageio.spec.rdf.v0_2.base_nodes import Author, Dependencies
from bioimageio.spec.shared.base_nodes import ImplicitInputShape, ImplicitOutputShape, NodeBase, URI

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore


FormatVersion = Literal["0.3.0", "0.3.1", "0.3.2"]  # newest format needs to be last (used in __init__.py)
Framework = Literal["pytorch", "tensorflow"]
Language = Literal["python", "java"]
PostprocessingName = Literal[
    "binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range", "scale_mean_variance"
]
PreprocessingName = Literal["binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range"]
WeightsFormat = Literal[
    "pytorch_state_dict", "pytorch_script", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"
]


@dataclass
class RunMode(NodeBase):
    name: str = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


@dataclass
class Preprocessing(NodeBase):
    name: PreprocessingName = missing
    kwargs: Dict[str, Any] = missing


@dataclass
class Postprocessing(NodeBase):
    name: PostprocessingName = missing
    kwargs: Dict[str, Any] = missing


@dataclass
class InputTensor(NodeBase):
    name: str = missing
    data_type: str = missing
    axes: str = missing
    shape: Union[List[int], ImplicitInputShape] = missing
    preprocessing: Union[_Missing, List[Preprocessing]] = missing
    description: Union[_Missing, str] = missing
    data_range: Union[_Missing, Tuple[float, float]] = missing


@dataclass
class OutputTensor(NodeBase):
    name: str = missing
    data_type: str = missing
    axes: str = missing
    shape: Union[List[int], ImplicitOutputShape] = missing
    halo: Union[_Missing, List[int]] = missing
    postprocessing: Union[_Missing, List[Postprocessing]] = missing
    description: Union[_Missing, str] = missing
    data_range: Union[_Missing, Tuple[float, float]] = missing


# to pass mypy:
# separate dataclass and abstract class as a workaround for abstract dataclasses
# from https://github.com/python/mypy/issues/5374#issuecomment-650656381
@dataclass
class _WeightsEntryBase(NodeBase):
    weights_format_name: ClassVar[str]  # human readable
    authors: Union[_Missing, List[Author]] = missing
    attachments: Union[_Missing, Dict] = missing
    parent: Union[_Missing, str] = missing
    sha256: Union[_Missing, str] = missing


class WeightsEntryBase(_WeightsEntryBase, ABC):
    @property
    @abstractmethod
    def source(self):
        raise NotImplementedError


@dataclass
class _KerasHdf5WeightsEntry(_WeightsEntryBase):
    weights_format_name = "Keras HDF5"
    tensorflow_version: Union[_Missing, distutils.version.StrictVersion] = missing


class KerasHdf5WeightsEntry(_KerasHdf5WeightsEntry, ABC):
    pass


@dataclass
class _OnnxWeightsEntry(_WeightsEntryBase):
    weights_format_name = "ONNX"
    opset_version: Union[_Missing, int] = missing


class OnnxWeightsEntry(_OnnxWeightsEntry, ABC):
    pass


@dataclass
class _PytorchStateDictWeightsEntry(_WeightsEntryBase):
    weights_format_name = "Pytorch State Dict"


class PytorchStateDictWeightsEntry(_PytorchStateDictWeightsEntry, ABC):
    pass


@dataclass
class _PytorchScriptWeightsEntry(_WeightsEntryBase):
    weights_format_name = "TorchScript"


class PytorchScriptWeightsEntry(_PytorchScriptWeightsEntry, ABC):
    pass


@dataclass
class _TensorflowJsWeightsEntry(_WeightsEntryBase):
    weights_format_name = "Tensorflow.js"
    tensorflow_version: Union[_Missing, distutils.version.StrictVersion] = missing


class TensorflowJsWeightsEntry(_TensorflowJsWeightsEntry, ABC):
    pass


@dataclass
class _TensorflowSavedModelBundleWeightsEntry(_WeightsEntryBase):
    weights_format_name = "Tensorflow Saved Model"
    tensorflow_version: Union[_Missing, distutils.version.StrictVersion] = missing
    # tag: Optional[str]  # todo: check schema. only valid for tensorflow_saved_model_bundle format


class TensorflowSavedModelBundleWeightsEntry(_TensorflowSavedModelBundleWeightsEntry, ABC):
    pass


@dataclass
class ModelParent(NodeBase):
    uri: URI = missing
    sha256: str = missing


# to pass mypy:
# separate dataclass and abstract class as a workaround for abstract dataclasses
# from https://github.com/python/mypy/issues/5374#issuecomment-650656381
@dataclass
class _Model(rdf.base_nodes._RDF):
    authors: List[Author] = missing  # type: ignore  # base RDF has List[Union[Author, str]], but should change soon
    dependencies: Union[_Missing, Dependencies] = missing
    format_version: FormatVersion = missing
    framework: Union[_Missing, Framework] = missing
    inputs: List[InputTensor] = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing
    language: Union[_Missing, Language] = missing
    license: str = missing
    links: Union[_Missing, List[str]] = missing
    outputs: List[OutputTensor] = missing
    packaged_by: Union[_Missing, List[Author]] = missing
    parent: Union[_Missing, ModelParent] = missing
    run_mode: Union[_Missing, RunMode] = missing
    sample_inputs: Union[_Missing, List[URI]] = missing
    sample_outputs: Union[_Missing, List[URI]] = missing
    sha256: Union[_Missing, str] = missing
    timestamp: datetime = missing
    type: Literal["model"] = missing


class Model(_Model, rdf.base_nodes.RDF, ABC):
    @property
    @abstractmethod
    def weights(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def source(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def test_inputs(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def test_outputs(self):
        raise NotImplementedError
