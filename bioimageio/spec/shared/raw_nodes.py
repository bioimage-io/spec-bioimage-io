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
class ResourceDescription(RawNode, base_nodes.ResourceDescriptionBase):
    pass


@dataclass
class URI(RawNode, base_nodes.URI_Base):
    pass


@dataclass
class Dependencies(RawNode, base_nodes.DependenciesBase):
    file: Union[URI, pathlib.Path] = missing


@dataclass
class ImplicitInputShape(RawNode, base_nodes.ImplicitInputShapeBase):
    pass


@dataclass
class ImplicitOutputShape(RawNode, base_nodes.ImplicitOutputShapeBase):
    pass


@dataclass
class ImportableModule(RawNode, base_nodes.ImportableModuleBase):
    pass


@dataclass
class ImportableSourceFile(RawNode, base_nodes.ImportableSourceFileBase):
    source_file: URI = missing
