""" raw nodes for the dataset RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
from dataclasses import dataclass

from marshmallow import missing

from bioimageio.spec.rdf.v0_2.raw_nodes import FormatVersion, RDF as _RDF

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

FormatVersion = FormatVersion


@dataclass
class Dataset(_RDF):
    type: Literal["dataset"] = missing
