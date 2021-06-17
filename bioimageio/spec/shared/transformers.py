import dataclasses
import importlib.util
import logging
import pathlib
import sys
import typing
import uuid
import warnings
from functools import singledispatch
from types import ModuleType
from urllib.parse import urlunparse
from urllib.request import url2pathname, urlretrieve

from marshmallow import ValidationError, missing

from . import BIOIMAGEIO_CACHE_PATH, fields, nodes, raw_nodes

GenericNode = typing.TypeVar("GenericNode", bound=raw_nodes.Node)


class Transformer:
    def transform(self, node: GenericNode) -> GenericNode:
        method = "transform_" + node.__class__.__name__

        transformer = getattr(self, method, self.generic_transformer)

        return transformer(node)

    def generic_transformer(self, node: GenericNode) -> GenericNode:
        return node

    def transform_list(self, node: list) -> list:
        return [self.transform(subnode) for subnode in node]

    def transform_dict(self, node: dict) -> dict:
        return {key: self.transform(value) for key, value in node.items()}


def iter_fields(node: dataclasses.dataclass):
    for field in dataclasses.fields(node):
        yield field.name, getattr(node, field.name)


class NodeVisitor:
    def visit(self, node: typing.Any) -> None:
        method = "visit_" + node.__class__.__name__

        visitor = getattr(self, method, self.generic_visit)

        visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        if isinstance(node, raw_nodes.Node):
            for field, value in iter_fields(node):
                self.visit(value)
        elif isinstance(node, list):
            [self.visit(subnode) for subnode in node]
        elif isinstance(node, dict):
            [self.visit(subnode) for subnode in node.values()]
        elif isinstance(node, tuple):
            assert not any(
                isinstance(subnode, raw_nodes.Node) or isinstance(subnode, list) or isinstance(subnode, dict)
                for subnode in node
            )


class NodeTransformer(Transformer):
    def generic_transformer(self, node: GenericNode) -> GenericNode:
        if isinstance(node, raw_nodes.Node):
            return dataclasses.replace(
                node,
                **{field.name: self.transform(getattr(node, field.name)) for field in dataclasses.fields(node)},  # noqa
            )
        else:
            return super().generic_transformer(node)


@dataclasses.dataclass
class LocalImportableModule(raw_nodes.ImportableModule):
    root_path: pathlib.Path = missing


@dataclasses.dataclass
class ResolvedImportablePath(raw_nodes.ImportablePath):
    pass


class UriNodeTransformer(NodeTransformer):
    def __init__(self, *, root_path: pathlib.Path):
        self.root_path = root_path

    def transform_URI(self, node: raw_nodes.URI) -> pathlib.Path:
        local_path = resolve_uri(node, root_path=self.root_path)
        return local_path

    def transform_ImportablePath(self, node: raw_nodes.ImportablePath) -> ResolvedImportablePath:
        return ResolvedImportablePath(
            filepath=(self.root_path / node.filepath).resolve(), callable_name=node.callable_name
        )

    def transform_ImportableModule(self, node: raw_nodes.ImportableModule) -> LocalImportableModule:
        return LocalImportableModule(**dataclasses.asdict(node), root_path=self.root_path)

    def _transform_Path(self, leaf: pathlib.Path):
        assert not leaf.is_absolute()
        return self.root_path / leaf

    def transform_PosixPath(self, leaf: pathlib.PosixPath) -> pathlib.Path:
        return self._transform_Path(leaf)

    def transform_WindowsPath(self, leaf: pathlib.WindowsPath) -> pathlib.Path:
        return self._transform_Path(leaf)


class SourceNodeTransformer(NodeTransformer):
    """
    Imports all source callables
    note: Requires previous transformation by UriNodeTransformer
    """

    class TemporaryInsertionIntoPythonPath:
        def __init__(self, path: str):
            self.path = path

        def __enter__(self):
            sys.path.insert(0, self.path)

        def __exit__(self, exc_type, exc_value, traceback):
            sys.path.remove(self.path)

    def transform_LocalImportableModule(self, node: LocalImportableModule) -> nodes.ImportedSource:
        with self.TemporaryInsertionIntoPythonPath(str(node.root_path)):
            module = importlib.import_module(node.module_name)

        return nodes.ImportedSource(factory=getattr(module, node.callable_name))

    @staticmethod
    def transform_ImportableModule(node):
        raise RuntimeError(
            "Encountered raw_nodes.ImportableModule in _SourceNodeTransformer. Apply _UriNodeTransformer first!"
        )

    @staticmethod
    def transform_ResolvedImportablePath(node: ResolvedImportablePath) -> nodes.ImportedSource:
        importlib_spec = importlib.util.spec_from_file_location(f"user_imports.{uuid.uuid4().hex}", node.filepath)
        dep = importlib.util.module_from_spec(importlib_spec)
        importlib_spec.loader.exec_module(dep)
        return nodes.ImportedSource(factory=getattr(dep, node.callable_name))

    @staticmethod
    def transform_ImportablePath(node):
        raise RuntimeError(
            "Encountered raw_nodes.ImportablePath in _SourceNodeTransformer. Apply _UriNodeTransformer first!"
        )


GenericRawNode = typing.TypeVar("GenericRawNode", bound=raw_nodes.Node)
GenericResolvedNode = typing.TypeVar("GenericResolvedNode", bound=nodes.Node)


class RawNodeTypeTransformer(NodeTransformer):
    def __init__(self, nodes_module: ModuleType):
        super().__init__()
        self.nodes = nodes_module

    def generic_transformer(self, node: GenericRawNode) -> GenericResolvedNode:
        if isinstance(node, raw_nodes.Node):
            resolved_data = {
                field.name: self.transform(getattr(node, field.name)) for field in dataclasses.fields(node)
            }
            resolved_node_type: typing.Type[GenericResolvedNode] = getattr(self.nodes, node.__class__.__name__)
            return resolved_node_type(**resolved_data)
        else:
            return super().generic_transformer(node)


@singledispatch
def resolve_uri(uri, root_path: pathlib.Path = pathlib.Path()):
    raise TypeError(type(uri))


@resolve_uri.register
def _(uri: raw_nodes.URI, root_path: pathlib.Path = pathlib.Path()) -> pathlib.Path:
    if uri.scheme == "":  # relative path
        if uri.authority or uri.query or uri.fragment:
            raise ValidationError(f"Invalid Path/URI: {uri}")

        local_path = root_path / uri.path
    elif uri.scheme == "file":
        if uri.authority or uri.query or uri.fragment:
            raise NotImplementedError(uri)

        local_path = pathlib.Path(url2pathname(uri.path))
    elif uri.scheme == "https":
        local_path = _download_uri_to_local_path(uri)
    else:
        raise ValueError(f"Unknown uri scheme {uri.scheme}")

    return local_path


@resolve_uri.register
def _(uri: str, root_path: pathlib.Path = pathlib.Path()) -> pathlib.Path:
    return resolve_uri(fields.URI().deserialize(uri), root_path)


@resolve_uri.register
def _(uri: pathlib.Path, root_path: pathlib.Path = pathlib.Path()) -> pathlib.Path:
    return resolve_uri(uri.as_uri(), root_path)


def download_uri_to_local_path(uri: typing.Union[raw_nodes.URI, str]) -> pathlib.Path:
    return resolve_uri(uri)


def _download_uri_to_local_path(uri: typing.Union[nodes.URI, raw_nodes.URI]) -> pathlib.Path:
    local_path = BIOIMAGEIO_CACHE_PATH / uri.scheme / uri.authority / uri.path.strip("/") / uri.query
    if local_path.exists():
        warnings.warn(f"found cached {local_path}. Skipping download of {uri}.")
    else:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        url_str = urlunparse([uri.scheme, uri.authority, uri.path, "", uri.query, uri.fragment])
        try:
            urlretrieve(url_str, str(local_path))
        except Exception:
            logging.getLogger("download").error("Failed to download %s", uri)
            raise

    return local_path


def resolve_raw_node_to_node(raw_node: raw_nodes.Node, root_path: pathlib.Path, nodes_module: ModuleType) -> nodes.Node:
    """resolve all uris and sources"""
    node = UriNodeTransformer(root_path=root_path).transform(raw_node)
    node = SourceNodeTransformer().transform(node)
    node = RawNodeTypeTransformer(nodes_module).transform(node)
    return node
