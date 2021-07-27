import distutils.version
from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Tuple, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.rdf import v0_2 as rdf
from bioimageio.spec.rdf.v0_2.raw_nodes import Author, Badge, CiteEntry, Dependencies
from bioimageio.spec.shared.raw_nodes import (
    ImplicitInputShape,
    ImplicitOutputShape,
    ImportableModule,
    ImportableSourceFile,
    Node,
    URI,
)

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # type: ignore


FormatVersion = Literal["0.3.0", "0.3.1", "0.3.2"]  # newest format needs to be last (used in __init__.py)

# same as general RDF; reassign to use imported classes
Badge = Badge
CiteEntry = CiteEntry
Dependencies = Dependencies


# overwritten general RDF
Type = Literal["model"]

# model specific
Axes = str
Framework = Literal["pytorch", "tensorflow"]
ImportableSource = Union[ImportableModule, ImportableSourceFile]
Language = Literal["python", "java"]
PostprocessingName = Literal[
    "binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range", "scale_mean_variance"
]
PreprocessingName = Literal["binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range"]
WeightsFormat = Literal[
    "pytorch_state_dict", "pytorch_script", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"
]


@dataclass
class RunMode(Node):
    name: str = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


@dataclass
class Preprocessing:
    name: PreprocessingName = missing
    kwargs: Dict[str, Any] = missing


@dataclass
class Postprocessing:
    name: PostprocessingName = missing
    kwargs: Dict[str, Any] = missing


@dataclass
class InputTensor:
    name: str = missing
    data_type: str = missing
    axes: Axes = missing
    shape: Union[List[int], ImplicitInputShape] = missing
    preprocessing: Union[_Missing, List[Preprocessing]] = missing
    description: Union[_Missing, str] = missing
    data_range: Union[_Missing, Tuple[float, float]] = missing


@dataclass
class OutputTensor:
    name: str = missing
    data_type: str = missing
    axes: Axes = missing
    shape: Union[List[int], ImplicitOutputShape] = missing
    halo: Union[_Missing, List[int]] = missing
    postprocessing: Union[_Missing, List[Postprocessing]] = missing
    description: Union[_Missing, str] = missing
    data_range: Union[_Missing, Tuple[float, float]] = missing


@dataclass
class WeightsEntryBase(Node):
    weights_format_name: ClassVar[str]  # human readable
    authors: Union[_Missing, List[Author]] = missing
    attachments: Union[_Missing, Dict] = missing
    parent: Union[_Missing, str] = missing
    sha256: Union[_Missing, str] = missing
    source: URI = missing


@dataclass
class KerasHdf5WeightsEntry(WeightsEntryBase):
    weights_format_name = "Keras HDF5"
    tensorflow_version: Union[_Missing, distutils.version.StrictVersion] = missing


@dataclass
class OnnxWeightsEntry(WeightsEntryBase):
    weights_format_name = "ONNX"
    opset_version: Union[_Missing, int] = missing


@dataclass
class PytorchStateDictWeightsEntry(WeightsEntryBase):
    weights_format_name = "Pytorch State Dict"


@dataclass
class PytorchScriptWeightsEntry(WeightsEntryBase):
    weights_format_name = "TorchScript"


@dataclass
class TensorflowJsWeightsEntry(WeightsEntryBase):
    weights_format_name = "Tensorflow.js"
    tensorflow_version: Union[_Missing, distutils.version.StrictVersion] = missing


@dataclass
class TensorflowSavedModelBundleWeightsEntry(WeightsEntryBase):
    weights_format_name = "Tensorflow Saved Model"
    tensorflow_version: Union[_Missing, distutils.version.StrictVersion] = missing
    # tag: Optional[str]  # todo: check schema. only valid for tensorflow_saved_model_bundle format


WeightsEntry = Union[
    PytorchStateDictWeightsEntry,
    PytorchScriptWeightsEntry,
    KerasHdf5WeightsEntry,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
    OnnxWeightsEntry,
]


@dataclass
class ModelParent(Node):
    uri: URI = missing
    sha256: str = missing


@dataclass
class Model(rdf.raw_nodes.RDF):
    authors: List[Author] = missing  # type: ignore  # base RDF has List[Union[Author, str]], but should change soon
    dependencies: Union[_Missing, Dependencies] = missing
    format_version: FormatVersion = missing
    framework: Union[_Missing, Framework] = missing
    inputs: List[InputTensor] = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing
    language: Union[_Missing, Language] = missing
    license: str = missing
    outputs: List[OutputTensor] = missing
    packaged_by: Union[_Missing, List[Author]] = missing
    parent: Union[_Missing, ModelParent] = missing
    run_mode: Union[_Missing, RunMode] = missing
    sample_inputs: Union[_Missing, List[URI]] = missing
    sample_outputs: Union[_Missing, List[URI]] = missing
    sha256: Union[_Missing, str] = missing
    source: Union[_Missing, ImportableSource] = missing
    test_inputs: List[URI] = missing
    test_outputs: List[URI] = missing
    timestamp: datetime = missing
    weights: Dict[WeightsFormat, WeightsEntry] = missing
