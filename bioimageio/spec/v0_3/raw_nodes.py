import distutils.version
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, NewType, Tuple, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.shared.raw_nodes import (
    ImplicitInputShape,
    ImplicitOutputShape,
    ImportableModule,
    ImportablePath,
    Node,
    URI,
)

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args


# Ideally only the current format version is valid.
# Older formats may be converter through `bioimageio.spec.utils.maybe_convert`,
# such that we only need to support the most up-to-date version.
FormatVersion = Literal["0.3.0", "0.3.1", "0.3.2"]  # newest format needs to be last (used in spec.__init__.py)
latest_version = get_args(FormatVersion)[-1]
ManifestFormatVersion = Literal["0.1.0", "0.2.0"]  # newest format expected to be last

PreprocessingName = Literal["binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range"]
PostprocessingName = Literal[
    "binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range", "scale_mean_variance"
]
Language = Literal["python", "java"]
Framework = Literal["scikit-learn", "pytorch", "tensorflow"]
WeightsFormat = Literal[
    "pickle",
    "pytorch_state_dict",
    "pytorch_script",
    "keras_hdf5",
    "tensorflow_js",
    "tensorflow_saved_model_bundle",
    "onnx",
]
Type = Literal["model"]

Dependencies = NewType("Dependencies", str)
Axes = NewType("Axes", str)


@dataclass
class Author(Node):
    name: str = missing
    affiliation: Union[_Missing, str] = missing
    orcid: Union[_Missing, str] = missing


ImportableSource = Union[ImportableModule, ImportablePath]


@dataclass
class CiteEntry(Node):
    text: str = missing
    doi: Union[_Missing, str] = missing
    url: Union[_Missing, str] = missing


@dataclass
class RunMode(Node):
    name: str = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


@dataclass
class RDF(Node):
    attachments: Union[_Missing, Dict[str, Any]] = missing
    authors: List[Author] = missing
    cite: List[CiteEntry] = missing
    config: Union[_Missing, dict] = missing
    covers: Union[_Missing, List[URI]] = missing
    dependencies: Union[_Missing, Dependencies] = missing
    description: str = missing
    documentation: Path = missing
    format_version: FormatVersion = missing
    framework: Union[_Missing, Framework] = missing
    git_repo: Union[_Missing, str] = missing
    language: Union[_Missing, Language] = missing
    license: str = missing
    name: str = missing
    run_mode: Union[_Missing, RunMode] = missing
    tags: List[str] = missing
    timestamp: datetime = missing
    type: Type = missing
    version: Union[_Missing, distutils.version.StrictVersion] = missing


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
class WeightsEntry(Node):
    authors: Union[_Missing, List[Author]] = missing
    attachments: Union[_Missing, Dict] = missing
    parent: Union[_Missing, str] = missing
    # ONNX specific
    opset_version: Union[_Missing, int] = missing
    # tag: Optional[str]  # todo: check schema. only valid for tensorflow_saved_model_bundle format
    # todo: check schema. only valid for tensorflow_saved_model_bundle format
    sha256: Union[_Missing, str] = missing
    source: URI = missing
    tensorflow_version: Union[_Missing, distutils.version.StrictVersion] = missing


@dataclass
class ModelParent(Node):
    uri: URI = missing
    sha256: str = missing


@dataclass
class Model(RDF):
    inputs: List[InputTensor] = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing
    outputs: List[OutputTensor] = missing
    packaged_by: Union[_Missing, List[Author]] = missing
    parent: Union[_Missing, ModelParent] = missing
    sample_inputs: Union[_Missing, List[URI]] = missing
    sample_outputs: Union[_Missing, List[URI]] = missing
    sha256: Union[_Missing, str] = missing
    source: Union[_Missing, ImportableSource] = missing
    test_inputs: List[URI] = missing
    test_outputs: List[URI] = missing
    type: Type = "model"
    weights: Dict[WeightsFormat, WeightsEntry] = missing


# Manifest
BioImageIoManifest = dict
BioImageIoManifestModelEntry = dict
BioImageIoManifestNotebookEntry = dict
Badge = dict
