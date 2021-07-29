import dataclasses
import distutils.version
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.shared.raw_nodes import Dependencies, Node, URI

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # type: ignore


FormatVersion = Literal["0.2.0"]  # newest format needs to be last (used to determine latest format version)

Framework = Literal["pytorch", "tensorflow"]
Language = Literal["python", "java"]
PreprocessingName = Literal["binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range"]
PostprocessingName = Literal[
    "binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range", "scale_mean_variance"
]
Type = str
WeightsFormat = Literal[
    "pytorch_state_dict", "pytorch_script", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"
]

# reassign to use imported classes
Dependencies = Dependencies


@dataclass
class CiteEntry(Node):
    text: str = missing
    doi: Union[_Missing, str] = missing
    url: Union[_Missing, str] = missing


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
    format_version: FormatVersion = missing
    git_repo: Union[_Missing, str] = missing
    license: Union[_Missing, str] = missing
    links: List[str] = missing
    name: str = missing
    tags: List[str] = missing
    type: Type = missing
    version: Union[_Missing, distutils.version.StrictVersion] = missing

    def __init__(self, **kwargs):  # todo: improve signature
        field_names = set(f.name for f in dataclasses.fields(self))
        known_kwargs = {k: v for k, v in kwargs.items() if k in field_names}
        for k, v in known_kwargs.items():
            setattr(self, k, v)
        unknown_kwargs = {k: v for k, v in kwargs.items() if k not in field_names}
        warnings.warn(f"discarding unknown kwargs: {unknown_kwargs}")

    def __post_init__(self):
        if self.type is missing:
            self.type = self.__class__.__name__.lower()  # noqa


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
