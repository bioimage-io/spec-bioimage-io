import packaging.version
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Tuple, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.rdf.v0_2.raw_nodes import Author, Maintainer, RDF
from bioimageio.spec.shared.raw_nodes import (
    Dependencies,
    ImplicitOutputShape,
    ImportableModule,
    ImportableSourceFile,
    ParametrizedInputShape,
    RawNode,
    URI,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

# reassign to use imported classes
Maintainer = Maintainer

FormatVersion = Literal[
    "0.3.0", "0.3.1", "0.3.2", "0.3.3", "0.3.4", "0.3.5", "0.3.6"
]  # newest format needs to be last (used in __init__.py)
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
class RunMode(RawNode):
    name: str = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


@dataclass
class Preprocessing(RawNode):
    name: PreprocessingName = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


@dataclass
class Postprocessing(RawNode):
    name: PostprocessingName = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


@dataclass
class InputTensor(RawNode):
    name: str = missing
    data_type: str = missing
    axes: str = missing
    shape: Union[List[int], ParametrizedInputShape] = missing
    preprocessing: Union[_Missing, List[Preprocessing]] = missing
    description: Union[_Missing, str] = missing
    data_range: Union[_Missing, Tuple[float, float]] = missing


@dataclass
class OutputTensor(RawNode):
    name: str = missing
    data_type: str = missing
    axes: str = missing
    shape: Union[List[int], ImplicitOutputShape] = missing
    halo: Union[_Missing, List[int]] = missing
    postprocessing: Union[_Missing, List[Postprocessing]] = missing
    description: Union[_Missing, str] = missing
    data_range: Union[_Missing, Tuple[float, float]] = missing


@dataclass
class _WeightsEntryBase(RawNode):
    _include_in_package = ("source",)
    weights_format_name: ClassVar[str]  # human readable
    authors: Union[_Missing, List[Author]] = missing
    attachments: Union[_Missing, Dict] = missing
    parent: Union[_Missing, str] = missing
    sha256: Union[_Missing, str] = missing
    source: Union[URI, Path] = missing


@dataclass
class KerasHdf5WeightsEntry(_WeightsEntryBase):
    weights_format_name = "Keras HDF5"
    tensorflow_version: Union[_Missing, packaging.version.Version] = missing


@dataclass
class OnnxWeightsEntry(_WeightsEntryBase):
    weights_format_name = "ONNX"
    opset_version: Union[_Missing, int] = missing


@dataclass
class PytorchStateDictWeightsEntry(_WeightsEntryBase):
    weights_format_name = "Pytorch State Dict"


@dataclass
class PytorchScriptWeightsEntry(_WeightsEntryBase):
    weights_format_name = "TorchScript"


@dataclass
class TensorflowJsWeightsEntry(_WeightsEntryBase):
    weights_format_name = "Tensorflow.js"
    tensorflow_version: Union[_Missing, packaging.version.Version] = missing


@dataclass
class TensorflowSavedModelBundleWeightsEntry(_WeightsEntryBase):
    weights_format_name = "Tensorflow Saved Model"
    tensorflow_version: Union[_Missing, packaging.version.Version] = missing
    # tag: Union[_Missing, str] = missing  # todo: do we need the tag??


WeightsEntry = Union[
    KerasHdf5WeightsEntry,
    OnnxWeightsEntry,
    PytorchScriptWeightsEntry,
    PytorchStateDictWeightsEntry,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
]

ImportableSource = Union[ImportableSourceFile, ImportableModule]


@dataclass
class ModelParent(RawNode):
    uri: Union[URI, Path] = missing
    sha256: str = missing


@dataclass
class Model(RDF):
    _include_in_package = ("covers", "documentation", "test_inputs", "test_outputs")

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
    sample_inputs: Union[_Missing, List[Union[URI, Path]]] = missing
    sample_outputs: Union[_Missing, List[Union[URI, Path]]] = missing
    sha256: Union[_Missing, str] = missing
    timestamp: datetime = missing
    type: Literal["model"] = missing

    source: Union[_Missing, ImportableSource] = missing
    test_inputs: List[Union[URI, Path]] = missing
    test_outputs: List[Union[URI, Path]] = missing
    weights: Dict[WeightsFormat, WeightsEntry] = missing
