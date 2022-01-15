""" raw nodes for the collection RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
import distutils.version
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, NewType, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.rdf.v0_2.raw_nodes import Author, Badge, CiteEntry, Maintainer, RDF
from bioimageio.spec.shared.raw_nodes import RawNode, URI

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # type: ignore

FormatVersion = Literal[
    "0.2.0", "0.2.1", "0.2.2"
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
        authors: Union[_Missing, List[Author]] = missing,
        badges: Union[_Missing, List[Badge]] = missing,
        cite: Union[_Missing, List[CiteEntry]] = missing,
        config: Union[_Missing, dict] = missing,
        covers: Union[_Missing, List[Union[URI, Path]]] = missing,
        description: str,
        documentation: Union[_Missing, Path] = missing,
        git_repo: Union[_Missing, str] = missing,
        license: Union[_Missing, str] = missing,
        links: Union[_Missing, List[str]] = missing,
        maintainers: Union[_Missing, List[Maintainer]] = missing,
        tags: Union[_Missing, List[str]] = missing,
        # collection RDF
        collection: List[CollectionEntry],
        unknown: Dict[str, Any] = missing,
        **implicitly_unknown,
    ):
        self.collection = collection
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
            license=license,
            links=links,
            maintainers=maintainers,
            name=name,
            tags=tags,
            type=type,
            version=version,
        )
        self.unknown = unknown or {}
        self.unknown.update(implicitly_unknown)
