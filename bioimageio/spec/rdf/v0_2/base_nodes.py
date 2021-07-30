from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.shared.base_nodes import Dependencies, NodeBase, ResourceDescription, URI

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
WeightsFormat = Literal[
    "pytorch_state_dict", "pytorch_script", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"
]

# reassign to use imported classes
Dependencies = Dependencies


@dataclass
class CiteEntry(NodeBase):
    text: str = missing
    doi: Union[_Missing, str] = missing
    url: Union[_Missing, str] = missing


@dataclass
class Author(NodeBase):
    name: str = missing
    affiliation: Union[_Missing, str] = missing
    orcid: Union[_Missing, str] = missing


@dataclass
class Badge(NodeBase):
    label: str = missing
    icon: Union[_Missing, str] = missing
    url: Union[_Missing, URI] = missing


# to pass mypy:
# separate dataclass and abstract class as a workaround for abstract dataclasses
# from https://github.com/python/mypy/issues/5374#issuecomment-650656381
@dataclass
class _RDF(ResourceDescription):
    attachments: Union[_Missing, Dict[str, Any]] = missing
    authors: List[Union[str, Author]] = missing
    badges: Union[_Missing, List[Badge]] = missing
    cite: List[CiteEntry] = missing
    config: Union[_Missing, dict] = missing
    description: str = missing
    documentation: Path = missing
    format_version: FormatVersion = missing
    git_repo: Union[_Missing, str] = missing
    license: Union[_Missing, str] = missing
    links: Union[_Missing, List[str]] = missing
    tags: List[str] = missing

    def __post_init__(self):
        if self.type is missing:
            self.type = self.__class__.__name__.lower()

        super().__post_init__()


class RDF(_RDF, ABC):
    @property
    @abstractmethod
    def covers(self):
        raise NotImplementedError


# to pass mypy:
# separate dataclass and abstract class as a workaround for abstract dataclasses
# from https://github.com/python/mypy/issues/5374#issuecomment-650656381
@dataclass
class _CollectionEntry(NodeBase):
    id: str = missing
    links: Union[_Missing, List[str]] = missing


class CollectionEntry(_CollectionEntry, ABC):
    @property
    @abstractmethod
    def source(self):
        raise NotImplementedError


class ModelCollectionEntry(CollectionEntry, ABC):
    @property
    @abstractmethod
    def download_url(self):
        raise NotImplementedError


# to pass mypy:
# separate dataclass and abstract class as a workaround for abstract dataclasses
# from https://github.com/python/mypy/issues/5374#issuecomment-650656381
@dataclass
class _Collection(_RDF):
    application: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    collection: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    model: Union[_Missing, List[ModelCollectionEntry]] = missing
    dataset: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    notebook: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing


class Collection(_Collection, RDF, ABC):
    pass
