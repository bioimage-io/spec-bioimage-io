""" raw nodes for the workflow RDF spec

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
from dataclasses import dataclass
from typing import List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.rdf.v0_2.raw_nodes import FormatVersion, RDF as _RDF
from bioimageio.spec.shared.raw_nodes import RawNode

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # type: ignore

FormatVersion = FormatVersion
ParameterType = Literal["tensor", "int", "float", "string", "boolean", "list", "dict", "any"]

DefaultType = Union[int, float, str, bool, list, dict, None]
# mapping of types of possible default values
DEFAULT_TYPE_NAME_MAP = {
    int: "int",
    float: "float",
    str: "string",
    bool: "boolean",
    list: "list",
    dict: "dict",
    None: "null",
}

# unit names from https://ngff.openmicroscopy.org/latest/#axes-md
SpaceUnit = Literal[
    "angstrom",
    "attometer",
    "centimeter",
    "decimeter",
    "exameter",
    "femtometer",
    "foot",
    "gigameter",
    "hectometer",
    "inch",
    "kilometer",
    "megameter",
    "meter",
    "micrometer",
    "mile",
    "millimeter",
    "nanometer",
    "parsec",
    "petameter",
    "picometer",
    "terameter",
    "yard",
    "yoctometer",
    "yottameter",
    "zeptometer",
    "zettameter",
]

TimeUnit = Literal[
    "attosecond",
    "centisecond",
    "day",
    "decisecond",
    "exasecond",
    "femtosecond",
    "gigasecond",
    "hectosecond",
    "hour",
    "kilosecond",
    "megasecond",
    "microsecond",
    "millisecond",
    "minute",
    "nanosecond",
    "petasecond",
    "picosecond",
    "second",
    "terasecond",
    "yoctosecond",
    "yottasecond",
    "zeptosecond",
    "zettasecond",
]

# this Axis definition is compatible with the NGFF draft from October 24, 2022
# https://ngff.openmicroscopy.org/latest/#axes-md
AxisType = Literal["batch", "channel", "index", "time", "space"]
ArbitraryAxes = Literal["arbitrary"]


@dataclass
class Axis:
    type: AxisType = missing
    name: Union[_Missing, str, List[str]] = missing
    description: Union[_Missing, str] = missing
    unit: Union[_Missing, SpaceUnit, TimeUnit, str, List[str]] = missing
    step: Union[_Missing, int] = missing


@dataclass
class Parameter(RawNode):
    name: str = missing
    type: ParameterType = missing
    description: Union[_Missing, str] = missing
    axes: Union[_Missing, List[Axis], ArbitraryAxes] = missing


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
class Workflow(_RDF):
    type: Literal["workflow"] = missing

    inputs: List[Input] = missing
    options: List[Option] = missing
    outputs: List[Output] = missing
