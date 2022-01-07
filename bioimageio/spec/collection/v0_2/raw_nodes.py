""" raw nodes for the collection RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
from dataclasses import dataclass
from typing import Any, Dict, List, NewType, Union

from marshmallow import missing

from bioimageio.spec.rdf.v0_2.raw_nodes import RDF
from bioimageio.spec.shared.raw_nodes import RawNode, URI

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # type: ignore

FormatVersion = Literal[
    "0.2.0", "0.2.1", "0.2.2"
]  # newest format needs to be last (used to determine latest format version)


RDF_Update = NewType("RDF_Update", Dict[str, Any])


@dataclass
class CollectionEntry(RawNode):
    """ """

    source: URI = missing
    id: str = missing
    rdf_update: RDF_Update = missing

    def __init__(self, source=missing, id_=missing, **rdf_update):
        self.source = source
        self.id = id_
        self.rdf_update = RDF_Update(rdf_update)
        super().__init__()


@dataclass
class Collection(RDF):
    collection: List[Union[RDF_Update, CollectionEntry]] = missing
