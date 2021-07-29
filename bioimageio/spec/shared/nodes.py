"""shared nodes that shared transformer act on"""
import dataclasses
import pathlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Union

from marshmallow import missing

from . import base_nodes

try:
    from typing import get_args, get_origin
except ImportError:
    from typing_extensions import get_args, get_origin


@dataclass
class Node(base_nodes.NodeBase):
    def __post_init__(self):
        for f in dataclasses.fields(self):
            if getattr(self, f.name) is missing and (
                get_origin(f.type) is not Union or not isinstance(missing, get_args(f.type))
            ):
                raise TypeError(f"{self.__class__}.__init__() missing required argument: '{f.name}'")


@dataclass
class ResourceDescription(Node, base_nodes.ResourceDescriptionBase):
    pass


class URI(Node, base_nodes.URI_Base):
    pass


class ImplicitInputShape(Node, base_nodes.ImplicitInputShapeBase):
    pass


class ImplicitOutputShape(Node, base_nodes.ImplicitOutputShapeBase):
    pass


@dataclass
class Dependencies(Node, base_nodes.DependenciesBase):
    file: pathlib.Path = missing


@dataclass
class LocalImportableModule(Node, base_nodes.ImportableModuleBase):
    """intermediate between raw_nodes.ImportableModule and nodes.ImportedSource. Used by SourceNodeTransformer"""

    root_path: pathlib.Path = missing


@dataclass
class ResolvedImportableSourceFile(Node, base_nodes.ImportableSourceFileBase):
    """intermediate between raw_nodes.ImportableSourceFile and nodes.ImportedSource. Used by SourceNodeTransformer"""

    source_file: pathlib.Path = missing


#
# only (non-raw) nodes, no base
#
@dataclass
class ImportedSource(Node):
    factory: Callable

    def __call__(self, *args, **kwargs):
        return self.factory(*args, **kwargs)
