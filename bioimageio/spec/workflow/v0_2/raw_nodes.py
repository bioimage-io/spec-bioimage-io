""" raw nodes for the dataset RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.rdf.v0_2.raw_nodes import FormatVersion, RDF as _RDF, URI
from bioimageio.spec.shared.raw_nodes import RawNode

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # type: ignore

FormatVersion = FormatVersion
ParameterType = Literal["tensor", "int", "float", "string", "boolean", "list", "dict", "any"]
DefaultType = Union[int, float, str, bool, list, dict, None]
TYPE_NAME_MAP = {int: "int", float: "float", str: "string", bool: "boolean", list: "list", dict: "dict", None: "null"}


@dataclass
class Parameter(RawNode):
    name: str = missing
    type: ParameterType = missing
    description: Union[_Missing, str] = missing
    axes: Union[_Missing, str] = missing


@dataclass
class Input(Parameter):
    pass


@dataclass
class Option(Parameter):
    default: Union[_Missing, DefaultType] = missing


@dataclass
class Output(Parameter):
    pass


@dataclass
class Step(RawNode):
    id: Union[_Missing, str] = missing
    op: str = missing
    inputs: Union[_Missing, List[Any], Dict[str, Any]] = missing
    outputs: Union[_Missing, List[str]] = missing


@dataclass
class Workflow(_RDF):
    type: Literal["workflow"] = missing

    inputs: List[Input] = missing
    options: List[Option] = missing
    outputs: List[Output] = missing

    steps: List[Step] = missing
    test_steps: List[Step] = missing
