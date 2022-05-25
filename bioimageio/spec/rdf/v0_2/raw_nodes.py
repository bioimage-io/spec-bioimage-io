""" raw nodes for the general RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
import dataclasses
import pathlib

import packaging.version
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.shared.raw_nodes import RawNode, ResourceDescription, URI

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # type: ignore

FormatVersion = Literal[
    "0.2.0", "0.2.1", "0.2.2", "0.2.3"
]  # newest format needs to be last (used to determine latest format version)


@dataclass(init=False)
class Attachments(RawNode):
    _include_in_package = ("files",)

    files: Union[_Missing, List[Union[Path, URI]]] = missing
    unknown: Dict[str, Any] = missing

    def __init__(
        self,
        files: Union[_Missing, List[Union[Path, URI]]] = missing,
        unknown: Dict[str, Any] = missing,
        **implicitly_unknown,
    ):
        self.files = files
        self.unknown = unknown or {}
        self.unknown.update(implicitly_unknown)
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
class CiteEntry(RawNode):
    text: str = missing
    doi: Union[_Missing, str] = missing
    url: Union[_Missing, str] = missing


@dataclass
class Badge(RawNode):
    label: str = missing
    icon: Union[_Missing, str] = missing
    url: Union[_Missing, URI, Path] = missing


@dataclass
class RDF(ResourceDescription):
    attachments: Union[_Missing, Attachments] = missing
    authors: Union[_Missing, List[Author]] = missing
    badges: Union[_Missing, List[Badge]] = missing
    cite: Union[_Missing, List[CiteEntry]] = missing
    config: Union[_Missing, dict] = missing
    covers: Union[_Missing, List[Union[URI, Path]]] = missing
    description: str = missing
    documentation: Union[_Missing, Path, URI] = missing
    download_url: Union[_Missing, Path, URI] = missing
    format_version: FormatVersion = missing
    git_repo: Union[_Missing, str] = missing
    id: Union[_Missing, str] = missing
    icon: Union[_Missing, str] = missing
    license: Union[_Missing, str] = missing
    links: Union[_Missing, List[str]] = missing
    maintainers: Union[_Missing, List[Maintainer]] = missing
    rdf_source: Union[_Missing, URI] = missing
    source: Union[_Missing, URI, Path] = missing
    tags: Union[_Missing, List[str]] = missing

    # manual __init__ to allow for unknown kwargs
    def __init__(
        self,
        *,
        # ResourceDescription
        format_version: FormatVersion,
        name: str,
        type: str = missing,
        version: Union[_Missing, packaging.version.Version] = missing,
        root_path: pathlib.Path = pathlib.Path(),
        # RDF
        attachments: Union[_Missing, Dict[str, Any]] = missing,
        authors: Union[_Missing, List[Author]] = missing,
        badges: Union[_Missing, List[Badge]] = missing,
        cite: Union[_Missing, List[CiteEntry]] = missing,
        config: Union[_Missing, dict] = missing,
        covers: Union[_Missing, List[Union[URI, Path]]] = missing,
        description: str,
        documentation: Union[_Missing, Path, URI] = missing,
        download_url: Union[_Missing, Path, URI] = missing,
        git_repo: Union[_Missing, str] = missing,
        id: Union[_Missing, str] = missing,
        icon: Union[_Missing, str] = missing,
        license: Union[_Missing, str] = missing,
        links: Union[_Missing, List[str]] = missing,
        maintainers: Union[_Missing, List[Maintainer]] = missing,
        rdf_source: Union[_Missing, URI] = missing,
        source: Union[_Missing, URI, Path] = missing,
        tags: Union[_Missing, List[str]] = missing,
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
        self.download_url = download_url
        self.git_repo = git_repo
        self.id = id
        self.icon = icon
        self.license = license
        self.links = links
        self.maintainers = maintainers
        self.rdf_source = rdf_source
        self.source = source
        self.tags = tags
        super().__init__(format_version=format_version, name=name, type=type, version=version, root_path=root_path)

        if unknown_kwargs:
            # make sure we didn't forget a defined field
            field_names = set(f.name for f in dataclasses.fields(self))
            for uk in unknown_kwargs:
                assert uk not in field_names, uk

            warnings.warn(f"discarding unknown RDF fields: {unknown_kwargs}")

    def __post_init__(self):
        if self.type is missing:
            self.type = self.__class__.__name__.lower()

        super().__post_init__()
