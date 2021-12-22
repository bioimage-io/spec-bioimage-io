""" raw nodes for the collection RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec import model as model_spec
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
    id: str = missing
    unknown: Dict[str, Any] = missing

    def __init__(self, source=missing, id_=missing, **unknown):
        self.source = source
        self.id = id_
        self.unknown = unknown
        super().__init__()


@dataclass
class Collection(RDF):
    application: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    # collection: Union[_Missing, List[Union[CollectionEntry, "Collection"]]] = missing
    model: Union[
        _Missing, List[Union[CollectionEntry, model_spec.v0_3.raw_nodes.Model, model_spec.v0_4.raw_nodes.Model]]
    ] = missing
    dataset: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
    notebook: Union[_Missing, List[Union[CollectionEntry, RDF]]] = missing
