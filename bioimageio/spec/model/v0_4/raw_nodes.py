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
    PostprocessingName,
    PreprocessingName,
    PytorchScriptWeightsEntry,
    RunMode,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
    WeightsFormat,
    _WeightsEntryBase,
)
from bioimageio.spec.rdf.v0_2.raw_nodes import Author, Badge, CiteEntry, Dependencies, RDF
from bioimageio.spec.shared.raw_nodes import (
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
Badge = Badge
CiteEntry = CiteEntry
ImplicitOutputShape = ImplicitOutputShape
ParametrizedInputShape = ParametrizedInputShape
PostprocessingName = PostprocessingName
PreprocessingName = PreprocessingName

FormatVersion = Literal["0.4.0"]  # newest format needs to be last (used in __init__.py)

ImportableSource = Union[ImportableSourceFile, ImportableModule]


@dataclass
class PytorchStateDictWeightsEntry(_WeightsEntryBase):
    weights_format_name = "Pytorch State Dict"
    architecture: ImportableSource = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


WeightsEntry = Union[
    KerasHdf5WeightsEntry,
    OnnxWeightsEntry,
    PytorchScriptWeightsEntry,
    PytorchStateDictWeightsEntry,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
]


@dataclass
class Model(RDF):
    _include_in_package = ("covers", "documentation", "test_inputs", "test_outputs")

    authors: List[Author] = missing  # type: ignore  # base RDF has List[Union[Author, str]], but should change soon
    dependencies: Union[_Missing, Dependencies] = missing
    format_version: FormatVersion = missing
    inputs: List[InputTensor] = missing
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

    test_inputs: List[Union[URI, Path]] = missing
    test_outputs: List[Union[URI, Path]] = missing
    weights: Dict[WeightsFormat, WeightsEntry] = missing
