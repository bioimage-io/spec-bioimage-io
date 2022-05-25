""" raw nodes for the collection RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
import pathlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

import packaging.version
from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.rdf.v0_2.raw_nodes import Author, Badge, CiteEntry, Maintainer, RDF
from bioimageio.spec.shared.raw_nodes import RawNode, URI

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # type: ignore

FormatVersion = Literal[
    "0.2.0", "0.2.1", "0.2.2", "0.2.3"
]  # newest format needs to be last (used to determine latest format version)


@dataclass
class CollectionEntry(RawNode):
    rdf_source: Union[_Missing, URI] = missing
    rdf_update: Dict[str, Any] = missing

    def __init__(
        self, rdf_source: Union[_Missing, URI] = missing, rdf_update: Dict[str, Any] = missing, **implicit_rdf_update
    ):
        self.rdf_source = rdf_source
        self.rdf_update = rdf_update or {}
        self.rdf_update.update(implicit_rdf_update)
        super().__init__()


@dataclass
class Collection(RDF):
    collection: List[CollectionEntry] = missing
    unknown: Dict[str, Any] = missing
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
        git_repo: Union[_Missing, str] = missing,
        id: Union[_Missing, str] = missing,
        icon: Union[_Missing, str] = missing,
        license: Union[_Missing, str] = missing,
        links: Union[_Missing, List[str]] = missing,
        maintainers: Union[_Missing, List[Maintainer]] = missing,
        rdf_source: Union[_Missing, URI] = missing,
        source: Union[_Missing, URI, Path] = missing,
        tags: Union[_Missing, List[str]] = missing,
        # collection RDF
        collection: List[CollectionEntry],
        unknown: Dict[str, Any] = missing,
        **implicitly_unknown,
    ):
        self.collection = collection
        self.unknown = unknown or {}
        self.unknown.update(implicitly_unknown)
        super().__init__(
            attachments=attachments,
            authors=authors,
            badges=badges,
            cite=cite,
            config=config,
            covers=covers,
            description=description,
            documentation=documentation,
            format_version=format_version,
            git_repo=git_repo,
            icon=icon,
            id=id,
            license=license,
            links=links,
            maintainers=maintainers,
            name=name,
            rdf_source=rdf_source,
            root_path=root_path,
            source=source,
            tags=tags,
            type=type,
            version=version,
        )
