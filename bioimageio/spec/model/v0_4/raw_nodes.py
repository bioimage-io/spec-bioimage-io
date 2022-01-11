from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.model.v0_3.raw_nodes import (
    InputTensor,
    KerasHdf5WeightsEntry,
    ModelParent,
    OnnxWeightsEntry,
    OutputTensor,
    Postprocessing,
    PostprocessingName,
    Preprocessing,
    PreprocessingName,
    RunMode,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
    _WeightsEntryBase,
)
from bioimageio.spec.rdf.v0_2.raw_nodes import Author, Maintainer, RDF as _RDF
from bioimageio.spec.shared.raw_nodes import (
    Dependencies,
    ImplicitOutputShape,
    ImportableModule,
    ImportableSourceFile,
    ParametrizedInputShape,
    URI,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

# reassign to use imported classes
ImplicitOutputShape = ImplicitOutputShape
Maintainer = Maintainer
ParametrizedInputShape = ParametrizedInputShape
Postprocessing = Postprocessing
PostprocessingName = PostprocessingName
Preprocessing = Preprocessing
PreprocessingName = PreprocessingName

FormatVersion = Literal["0.4.0", "0.4.1", "0.4.2"]  # newest format needs to be last (used in __init__.py)
WeightsFormat = Literal[
    "pytorch_state_dict", "torchscript", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"
]

ImportableSource = Union[ImportableSourceFile, ImportableModule]


@dataclass
class PytorchStateDictWeightsEntry(_WeightsEntryBase):
    weights_format_name = "Pytorch State Dict"
    architecture: ImportableSource = missing
    architecture_sha256: Union[_Missing, str] = missing
    dependencies: Union[_Missing, Dependencies] = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


@dataclass
class TorchscriptWeightsEntry(_WeightsEntryBase):
    weights_format_name = "Torchscript"


WeightsEntry = Union[
    KerasHdf5WeightsEntry,
    OnnxWeightsEntry,
    PytorchStateDictWeightsEntry,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
    TorchscriptWeightsEntry,
]


@dataclass
class Model(_RDF):
    _include_in_package = ("covers", "documentation", "test_inputs", "test_outputs", "sample_inputs", "sample_outputs")

    format_version: FormatVersion = missing
    inputs: List[InputTensor] = missing
    license: str = missing
    outputs: List[OutputTensor] = missing
    packaged_by: Union[_Missing, List[Author]] = missing
    parent: Union[_Missing, ModelParent] = missing
    run_mode: Union[_Missing, RunMode] = missing
    sample_inputs: Union[_Missing, List[Union[URI, Path]]] = missing
    sample_outputs: Union[_Missing, List[Union[URI, Path]]] = missing
    timestamp: datetime = missing
    type: Literal["model"] = missing

    test_inputs: List[Union[URI, Path]] = missing
    test_outputs: List[Union[URI, Path]] = missing
    weights: Dict[WeightsFormat, WeightsEntry] = missing
