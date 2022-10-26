""" raw nodes for the dataset RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
from dataclasses import dataclass
from pathlib import Path

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.rdf.v0_2.raw_nodes import FormatVersion, RDF as _RDF, URI
from bioimageio.spec.shared.raw_nodes import RawNode

try:
    from typing import Any, Dict, List, Literal, Union
except ImportError:
    from typing_extensions import Literal  # type: ignore

FormatVersion = FormatVersion


@dataclass
class Tensor(RawNode):
    name: str = missing
    description: Union[_Missing, str] = missing


@dataclass
class Step(RawNode):
    id: Union[_Missing, str] = missing
    op: str = missing
    inputs: Union[_Missing, List[str]] = missing
    outputs: Union[_Missing, List[str]] = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


@dataclass
class Workflow(_RDF):
    type: Literal["workflow"] = missing

    inputs: List[Tensor] = missing
    outputs: List[Tensor] = missing

    test_inputs: List[Union[URI, Path]] = missing
    test_outputs: List[Union[URI, Path]] = missing

    steps: List[Step] = missing
