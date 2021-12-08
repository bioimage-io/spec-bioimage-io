""" raw nodes for the collection RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.rdf.v0_2.raw_nodes import FormatVersion, RDF
from bioimageio.spec.shared.raw_nodes import RawNode, URI

FormatVersion = FormatVersion  # format version is synced with general RDF
try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # type: ignore


@dataclass
class CollectionEntry(RawNode):
    source: URI = missing
    id_: str = missing
    links: Union[_Missing, List[str]] = missing
    unknown: Dict[str, Any] = missing

    def __init__(self, source=missing, id_=missing, links=missing, **unknown):
        self.source = source
        self.id_ = id_
        self.links = links
        self.unknown = unknown
        super().__init__()


@dataclass
class Collection(RDF):
    application: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    collection: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    model: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    dataset: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    notebook: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
