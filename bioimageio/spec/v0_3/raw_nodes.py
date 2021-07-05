import distutils.version
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Dict, List, NewType, Tuple, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec import v0_1
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


GeneralFormatVersion = Literal["0.2.0"]  # newest format needs to be last (used in spec.__init__.py)
ModelFormatVersion = Literal[  # type: ignore  # Param 1 of Literal cannot be of type "Any"
    v0_1.ModelFormatVersion, "0.3.0", "0.3.1", "0.3.2"  # newest format needs to be last (used in spec.__init__.py)
]
latest_version = get_args(ModelFormatVersion)[-1]


Dependencies = str
Framework = Literal["pytorch", "tensorflow"]
Language = Literal["python", "java"]
PreprocessingName = Literal["binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range"]
PostprocessingName = Literal[
    "binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range", "scale_mean_variance"
]
Type = Literal["model", "dataset", "application", "notebook"]
WeightsFormat = Literal[
    "pytorch_state_dict", "pytorch_script", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"
]


Axes = str


@dataclass
class CiteEntry(v0_1.raw_nodes.CiteEntry):
    pass


@dataclass
class Author(Node):
    name: str = missing
    affiliation: Union[_Missing, str] = missing
    orcid: Union[_Missing, str] = missing


@dataclass
class Badge(Node):
    label: str = missing
    icon: Union[_Missing, str] = missing
    url: Union[_Missing, URI] = missing


ImportableSource = Union[ImportableModule, ImportableSourceFile]


@dataclass
class RunMode(Node):
    name: str = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


@dataclass
class RDF(Node):
    attachments: Union[_Missing, Dict[str, Any]] = missing
    authors: List[Union[str, Author]] = missing
    badges: Union[_Missing, List[Badge]] = missing
    cite: List[CiteEntry] = missing
    config: Union[_Missing, dict] = missing
    covers: Union[_Missing, List[URI]] = missing
    description: str = missing
    documentation: Path = missing
    format_version: ModelFormatVersion = missing
    git_repo: Union[_Missing, str] = missing
    license: Union[_Missing, str] = missing
    links: List[str] = missing
    name: str = missing
    tags: List[str] = missing
    type: Type = missing
    version: Union[_Missing, distutils.version.StrictVersion] = missing

    def __post_init__(self):
        if self.type is missing:
            self.type = self.__class__.__name__.lower()  # noqa

        assert self.type in get_args(Type)


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
class Model(RDF):
    authors: List[Author] = missing  # type: ignore  # base RDF has List[Union[Author, str]], but should change soon
    dependencies: Union[_Missing, Dependencies] = missing
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


@dataclass
class CollectionEntry(Node):
    source: URI
    id: str
    links: Union[_Missing, List[str]] = missing


@dataclass
class ModelCollectionEntry(CollectionEntry):
    download_url: URI = missing


@dataclass
class Collection(RDF):
    application: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    collection: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    model: Union[_Missing, List[ModelCollectionEntry]] = missing
    dataset: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    notebook: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing


# deprecated Manifest  # todo: remove
BioImageIoManifest = dict
BioImageIoManifestModelEntry = dict
BioImageIoManifestNotebookEntry = dict
