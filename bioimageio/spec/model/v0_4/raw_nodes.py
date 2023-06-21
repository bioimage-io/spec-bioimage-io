import packaging.version
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.dataset.v0_2.raw_nodes import Dataset
from bioimageio.spec.model.v0_3.raw_nodes import (
    InputTensor,
    KerasHdf5WeightsEntry as KerasHdf5WeightsEntry03,
    OnnxWeightsEntry as OnnxWeightsEntry03,
    OutputTensor,
    Postprocessing,
    PostprocessingName,
    Preprocessing,
    PreprocessingName,
    RunMode,
    TensorflowJsWeightsEntry as TensorflowJsWeightsEntry03,
    TensorflowSavedModelBundleWeightsEntry as TensorflowSavedModelBundleWeightsEntry03,
    _WeightsEntryBase as _WeightsEntryBase03,
)
from bioimageio.spec.rdf.v0_2.raw_nodes import Author, Maintainer, RDF_Base as _RDF
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
ImplicitOutputShape = ImplicitOutputShape
InputTensor = InputTensor
Maintainer = Maintainer
OutputTensor = OutputTensor
ParametrizedInputShape = ParametrizedInputShape
Postprocessing = Postprocessing
PostprocessingName = PostprocessingName
Preprocessing = Preprocessing
PreprocessingName = PreprocessingName


@dataclass
class LinkedDataset(RawNode):
    id: str


@dataclass
class ModelParent(RawNode):
    id: Union[_Missing, str] = missing
    uri: Union[_Missing, URI, Path] = missing
    sha256: Union[_Missing, str] = missing


@dataclass
class Model(_RDF):
    _include_in_package = ("covers", "documentation", "test_inputs", "test_outputs", "sample_inputs", "sample_outputs")

    inputs: List[InputTensor] = missing
    license: str = missing
    outputs: List[OutputTensor] = missing
    packaged_by: Union[_Missing, List[Author]] = missing
    parent: Union[_Missing, ModelParent] = missing
    run_mode: Union[_Missing, RunMode] = missing
    sample_inputs: Union[_Missing, List[Union[URI, Path]]] = missing
    sample_outputs: Union[_Missing, List[Union[URI, Path]]] = missing
    test_inputs: List[Union[URI, Path]] = missing
    test_outputs: List[Union[URI, Path]] = missing
    timestamp: datetime = missing
    training_data: Union[_Missing, Dataset, LinkedDataset] = missing
    type: Literal["model"] = missing
    weights: Dict[WeightsFormat, WeightsEntry] = missing
