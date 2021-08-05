"""shared raw nodes that shared transformer act on"""
import dataclasses
import pathlib
from dataclasses import dataclass
from typing import ClassVar, Dict, Sequence, Union

from marshmallow import missing

from . import base_nodes


@dataclass
class RawNode(base_nodes.NodeBase):
    _include_in_package: ClassVar[Sequence[str]] = tuple()

    def __post_init__(self):
        field_names = [f.name for f in dataclasses.fields(self)]
        for incl_in_package in self._include_in_package:
            assert incl_in_package in field_names


@dataclass
class ResourceDescription(RawNode, base_nodes.ResourceDescription):
    pass


@dataclass
class URI(base_nodes.URI, RawNode):
    pass


@dataclass
class Dependencies(RawNode, base_nodes.Dependencies):
    file: Union[URI, pathlib.Path] = missing


@dataclass
class ImplicitInputShape(RawNode, base_nodes.ImplicitInputShape):
    pass


@dataclass
class ImplicitOutputShape(RawNode, base_nodes.ImplicitOutputShape):
    pass


@dataclass
class ImportableModule(RawNode, base_nodes.ImportableModule):
    pass


@dataclass
class ImportableSourceFile(RawNode, base_nodes.ImportableSourceFile):
    source_file: URI = missing


ImportableSource = Union[ImportableModule, ImportableSourceFile]
