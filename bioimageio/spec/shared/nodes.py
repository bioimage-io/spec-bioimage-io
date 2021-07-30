"""shared nodes that shared transformer act on"""
import pathlib
from collections.abc import Callable
from dataclasses import dataclass

from marshmallow import missing

from . import base_nodes

try:
    from typing import get_args, get_origin
except ImportError:
    from typing_extensions import get_args, get_origin


@dataclass
class Node(base_nodes.NodeBase):
    pass


@dataclass
class ResourceDescription(Node, base_nodes.ResourceDescription):
    pass


@dataclass
class URI(Node, base_nodes.URI):
    pass


@dataclass
class ImplicitInputShape(Node, base_nodes.ImplicitInputShape):
    pass


@dataclass
class ImplicitOutputShape(Node, base_nodes.ImplicitOutputShape):
    pass


@dataclass
class Dependencies(Node, base_nodes.Dependencies):
    file: pathlib.Path = missing


@dataclass
class LocalImportableModule(Node, base_nodes.ImportableModule):
    """intermediate between raw_nodes.ImportableModule and nodes.ImportedSource. Used by SourceNodeTransformer"""

    root_path: pathlib.Path = missing


@dataclass
class ResolvedImportableSourceFile(Node, base_nodes.ImportableSourceFile):
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
