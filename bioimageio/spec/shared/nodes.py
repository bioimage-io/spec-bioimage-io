"""shared nodes that shared transformer act on"""
import pathlib
from collections.abc import Callable
from dataclasses import dataclass

from marshmallow import missing

from . import raw_nodes

Node = raw_nodes.Node
URI = raw_nodes.URI
ImplicitInputShape = raw_nodes.ImplicitInputShape
ImplicitOutputShape = raw_nodes.ImplicitOutputShape


@dataclass
class LocalImportableModule(raw_nodes.ImportableModule):
    """intermediate between raw_nodes.ImportableModule and nodes.ImportedSource. Used by SourceNodeTransformer"""

    root_path: pathlib.Path = missing


@dataclass
class ImportedSource(Node):
    factory: Callable

    def __call__(self, *args, **kwargs):
        return self.factory(*args, **kwargs)


@dataclass
class ResolvedImportableSourceFile(Node):
    source_file: pathlib.Path
    callable_name: str
