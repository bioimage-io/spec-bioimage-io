""" raw nodes for the general RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
import dataclasses
import distutils.version
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.shared.raw_nodes import Dependencies, RawNode, ResourceDescription, URI

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
class CiteEntry(RawNode):
    text: str = missing
    doi: Union[_Missing, str] = missing
    url: Union[_Missing, str] = missing


@dataclass
class Author(RawNode):
    name: str = missing
    affiliation: Union[_Missing, str] = missing
    orcid: Union[_Missing, str] = missing


@dataclass
class Badge(RawNode):
    label: str = missing
    icon: Union[_Missing, str] = missing
    url: Union[_Missing, URI, Path] = missing


@dataclass
class RDF(ResourceDescription):
    attachments: Union[_Missing, Dict[str, Any]] = missing
    authors: List[Union[str, Author]] = missing
    badges: Union[_Missing, List[Badge]] = missing
    cite: List[CiteEntry] = missing
    config: Union[_Missing, dict] = missing
    covers: Union[_Missing, List[Union[URI, Path]]] = missing
    description: str = missing
    documentation: Path = missing
    format_version: FormatVersion = missing
    git_repo: Union[_Missing, str] = missing
    license: Union[_Missing, str] = missing
    links: Union[_Missing, List[str]] = missing
    tags: List[str] = missing

    # manual __init__ to allow for unknown kwargs
    def __init__(
        self,
        *,
        # ResourceDescription
        format_version: FormatVersion,
        name: str,
        type: str = missing,
        version: Union[_Missing, distutils.version.StrictVersion] = missing,
        # RDF
        attachments: Union[_Missing, Dict[str, Any]] = missing,
        authors: List[Union[str, Author]],
        badges: Union[_Missing, List[Badge]] = missing,
        cite: List[CiteEntry],
        config: Union[_Missing, dict] = missing,
        covers: Union[_Missing, List[Union[URI, Path]]] = missing,
        description: str,
        documentation: Path,
        git_repo: Union[_Missing, str] = missing,
        license: Union[_Missing, str] = missing,
        links: Union[_Missing, List[str]] = missing,
        tags: List[str],
        **unknown_kwargs,
    ):
        self.attachments = attachments
        self.authors = authors
        self.badges = badges
        self.cite = cite
        self.config = config
        self.covers = covers
        self.description = description
        self.documentation = documentation
        self.git_repo = git_repo
        self.license = license
        self.links = links
        self.tags = tags
        super().__init__(format_version=format_version, name=name, type=type, version=version)

        if unknown_kwargs:
            # make sure we didn't forget a defined field
            field_names = set(f.name for f in dataclasses.fields(self))
            for uk in unknown_kwargs:
                assert uk not in field_names

            warnings.warn(f"discarding unknown RDF fields: {unknown_kwargs}")

    def __post_init__(self):
        if self.type is missing:
            self.type = self.__class__.__name__.lower()

        super().__post_init__()


@dataclass
class CollectionEntry(RawNode):
    source: URI = missing
    id: str = missing
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
