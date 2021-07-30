"""shared raw nodes that shared transformer act on"""
import pathlib
from dataclasses import dataclass
from typing import Union

from marshmallow import missing

from . import base_nodes


@dataclass
class RawNode(base_nodes.NodeBase):
    pass


@dataclass
class ResourceDescription(RawNode, base_nodes.ResourceDescription):
    pass


@dataclass
class URI(RawNode, base_nodes.URI):
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
