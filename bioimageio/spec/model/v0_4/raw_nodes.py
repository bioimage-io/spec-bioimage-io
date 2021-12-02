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
    Postprocessing,
    Preprocessing,
    RunMode,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
    _WeightsEntryBase,
)
from bioimageio.spec.rdf.v0_2.raw_nodes import CiteEntry, Dependencies, RDF as _RDF
from bioimageio.spec.shared.raw_nodes import (
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
CiteEntry = CiteEntry
ImplicitOutputShape = ImplicitOutputShape
ParametrizedInputShape = ParametrizedInputShape
Postprocessing = Postprocessing
PostprocessingName = PostprocessingName
Preprocessing = Preprocessing
PreprocessingName = PreprocessingName

FormatVersion = Literal["0.4.0"]  # newest format needs to be last (used in __init__.py)
WeightsFormat = Literal[
    "pytorch_state_dict", "torchscript", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"
]

ImportableSource = Union[ImportableSourceFile, ImportableModule]


class Attachments(RawNode):  # note: not a dataclass due to the unknown fields; (fingers crossed for no bugs)
    def __init__(self, files: Union[_Missing, List[Union[Path, URI]]] = missing, **unknown):
        self.files = files
        self.unknown = unknown
        super().__init__()


@dataclass
class _Person(RawNode):
    name: Union[_Missing, str] = missing
    affiliation: Union[_Missing, str] = missing
    email: Union[_Missing, str] = missing
    github_user: Union[_Missing, str] = missing
    orcid: Union[_Missing, str] = missing


@dataclass
class Author(_Person):
    name: str = missing


@dataclass
class Maintainer(_Person):
    github_user: str = missing


@dataclass
class PytorchStateDictWeightsEntry(_WeightsEntryBase):
    weights_format_name = "Pytorch State Dict"
    architecture: ImportableSource = missing
    architecture_sha256: Union[_Missing, str] = missing
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

    attachments: Union[_Missing, Attachments] = missing
    authors: List[Author] = missing  # type: ignore  # base RDF has List[Union[Author, str]], but should change soon
    dependencies: Union[_Missing, Dependencies] = missing
    format_version: FormatVersion = missing
    inputs: List[InputTensor] = missing
    license: str = missing
    links: Union[_Missing, List[str]] = missing
    maintainers: Union[_Missing, List[Maintainer]] = missing
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
