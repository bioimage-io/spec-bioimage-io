import dataclasses
import importlib.util
import logging
import os
import pathlib
import sys
import typing
import warnings
from functools import singledispatch
from types import ModuleType
from urllib.request import url2pathname, urlretrieve

import requests
from marshmallow import ValidationError

from . import base_nodes, fields, nodes, raw_nodes
from .common import BIOIMAGEIO_CACHE_PATH
from .nodes import LocalImportableModule, ResolvedImportableSourceFile

GenericRawNode = typing.TypeVar("GenericRawNode", bound=raw_nodes.RawNode)
GenericRawRD = typing.TypeVar("GenericRawRD", bound=raw_nodes.ResourceDescription)
GenericResolvedNode = typing.TypeVar("GenericResolvedNode", bound=nodes.Node)
# GenericNode = typing.TypeVar("GenericNode", bound=base_nodes.NodeBase)
URI_Type = typing.TypeVar("URI_Type", bound=base_nodes.URI)
URI_Node = typing.Union[raw_nodes.URI, nodes.URI]
GenericNode = typing.Union[GenericRawNode, GenericResolvedNode]
# todo: improve GenericNode definition


def iter_fields(node: GenericNode):
    for field in dataclasses.fields(node):
        yield field.name, getattr(node, field.name)


class NodeVisitor:
    def visit(self, node: typing.Any) -> None:
        method = "visit_" + node.__class__.__name__

        visitor: typing.Callable[[typing.Any], typing.Any] = getattr(self, method, self.generic_visit)

        visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""

        if isinstance(node, (nodes.Node, raw_nodes.RawNode)):
            for field, value in iter_fields(node):
                self.visit(value)
        elif isinstance(node, base_nodes.NodeBase):
            raise TypeError(
                f"Encountered base node {node}. Base nodes should not be instantiated! "
                "Use raw_nodes.RawNode or nodes.Node instead."
            )
        elif isinstance(node, dict):
            [self.visit(subnode) for subnode in node.values()]
        elif isinstance(node, (tuple, list)):
            [self.visit(subnode) for subnode in node]


class UriNodeChecker(NodeVisitor):
    """raises FileNotFoundError for unavailable URIs and paths"""

    def __init__(self, *, root_path: os.PathLike):
        self.root_path = pathlib.Path(root_path)

    def visit_URI(self, node: URI_Node):
        if not uri_available(node, self.root_path):
            raise FileNotFoundError(node)

    def _visit_Path(self, leaf: pathlib.Path):
        if not leaf.exists():
            raise FileNotFoundError(leaf)

    def visit_PosixPath(self, leaf: pathlib.PosixPath):
        self._visit_Path(leaf)

    def visit_WindowsPath(self, leaf: pathlib.WindowsPath):
        self._visit_Path(leaf)


class Transformer:
    def transform(self, node: typing.Any) -> typing.Any:
        method = "transform_" + node.__class__.__name__

        transformer = getattr(self, method, self.generic_transformer)

        return transformer(node)

    def generic_transformer(self, node: typing.Any) -> typing.Any:
        return node

    def transform_list(self, node: list) -> list:
        return [self.transform(subnode) for subnode in node]

    def transform_dict(self, node: dict) -> dict:
        return {key: self.transform(value) for key, value in node.items()}


class NodeTransformer(Transformer):
    def generic_transformer(self, node: GenericNode) -> GenericNode:
        if isinstance(node, base_nodes.NodeBase):
            return dataclasses.replace(node, **{name: self.transform(value) for name, value in iter_fields(node)})
        else:
            return super().generic_transformer(node)


class UriNodeTransformer(NodeTransformer):
    def __init__(self, *, root_path: os.PathLike):
        self.root_path = pathlib.Path(root_path)

    def transform_URI(self, node: URI_Node) -> pathlib.Path:
        local_path = resolve_uri(node, root_path=self.root_path)
        return local_path

    def transform_ImportableSourceFile(self, node: base_nodes.ImportableSourceFile) -> ResolvedImportableSourceFile:
        return ResolvedImportableSourceFile(
            source_file=resolve_uri(node.source_file, self.root_path), callable_name=node.callable_name
        )

    def transform_ImportableModule(self, node: base_nodes.ImportableModule) -> LocalImportableModule:
        return LocalImportableModule(**dataclasses.asdict(node), root_path=self.root_path)

    def _transform_Path(self, leaf: pathlib.Path):
        return self.root_path / leaf

    def transform_PosixPath(self, leaf: pathlib.PosixPath) -> pathlib.Path:
        return self._transform_Path(leaf)

    def transform_WindowsPath(self, leaf: pathlib.WindowsPath) -> pathlib.Path:
        return self._transform_Path(leaf)


class PathToRemoteUriTransformer(NodeTransformer):
    def __init__(self, *, remote_source: URI_Type):
        remote_path = pathlib.PurePosixPath(remote_source.path).parent.as_posix()
        self.remote_root = dataclasses.replace(remote_source, path=remote_path, uri_string=None)

    def transform_URI(self, node: URI_Type) -> URI_Type:
        if node.scheme == "file":
            raise ValueError(f"Cannot create remote URI of absolute file path: {node}")

        if node.scheme == "":
            # make local relative path remote
            assert not node.authority
            assert not node.query
            assert not node.fragment

            path = pathlib.PurePosixPath(self.remote_root.path) / node.path
            node = dataclasses.replace(self.remote_root, path=path.as_posix(), uri_string=None)

        return node

    def _transform_Path(self, leaf: pathlib.Path):
        assert not leaf.is_absolute()
        return self.transform_URI(raw_nodes.URI(path=leaf.as_posix()))

    def transform_PosixPath(self, leaf: pathlib.PosixPath) -> raw_nodes.URI:
        return self._transform_Path(leaf)

    def transform_WindowsPath(self, leaf: pathlib.WindowsPath) -> raw_nodes.URI:
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
    def transform_ResolvedImportableSourceFile(node: ResolvedImportableSourceFile) -> nodes.ImportedSource:
        module_path = resolve_uri(node.source_file)
        module_name = f"module_from_source.{module_path.stem}"
        importlib_spec = importlib.util.spec_from_file_location(module_name, module_path)
        assert importlib_spec is not None
        dep = importlib.util.module_from_spec(importlib_spec)
        importlib_spec.loader.exec_module(dep)  # type: ignore  # todo: possible to use "loader.load_module"?
        return nodes.ImportedSource(factory=getattr(dep, node.callable_name))

    @staticmethod
    def transform_ImportablePath(node):
        raise RuntimeError(
            "Encountered raw_nodes.ImportableSourceFile in _SourceNodeTransformer. Apply _UriNodeTransformer first!"
        )


class RawNodeTypeTransformer(NodeTransformer):
    def __init__(self, nodes_module: ModuleType):
        super().__init__()
        self.nodes = nodes_module

    def generic_transformer(self, node: GenericRawNode) -> GenericResolvedNode:
        if isinstance(node, raw_nodes.RawNode):
            resolved_data = {
                field.name: self.transform(getattr(node, field.name)) for field in dataclasses.fields(node)
            }
            resolved_node_type: typing.Type[GenericResolvedNode] = getattr(self.nodes, node.__class__.__name__)
            return resolved_node_type(**resolved_data)  # type: ignore
        else:
            return super().generic_transformer(node)


@singledispatch
def resolve_uri(uri, root_path: os.PathLike = pathlib.Path()):
    raise TypeError(type(uri))


@resolve_uri.register
def _resolve_uri_uri_node(uri: base_nodes.URI, root_path: os.PathLike = pathlib.Path()) -> pathlib.Path:
    assert isinstance(uri, (raw_nodes.URI, nodes.URI))
    path_or_remote_uri = resolve_local_uri(uri, root_path)
    if isinstance(path_or_remote_uri, base_nodes.URI):
        local_path = _download_uri_to_local_path(path_or_remote_uri)
    elif isinstance(path_or_remote_uri, pathlib.Path):
        local_path = path_or_remote_uri
    else:
        raise TypeError(path_or_remote_uri)

    return local_path


@resolve_uri.register
def _resolve_uri_str(uri: str, root_path: os.PathLike = pathlib.Path()) -> pathlib.Path:
    return resolve_uri(fields.URI().deserialize(uri), root_path)


@resolve_uri.register
def _resolve_uri_path(uri: pathlib.Path, root_path: os.PathLike = pathlib.Path()) -> pathlib.Path:
    if not uri.is_absolute():
        uri = pathlib.Path(root_path).absolute() / uri

    return resolve_uri(uri.as_uri(), root_path)


@resolve_uri.register
def _resolve_uri_resolved_importable_path(
    uri: ResolvedImportableSourceFile, root_path: os.PathLike = pathlib.Path()
) -> ResolvedImportableSourceFile:
    return ResolvedImportableSourceFile(
        callable_name=uri.callable_name, source_file=resolve_uri(uri.source_file, root_path)
    )


@resolve_uri.register
def _resolve_uri_importable_path(
    uri: base_nodes.ImportableSourceFile, root_path: os.PathLike = pathlib.Path()
) -> ResolvedImportableSourceFile:
    return ResolvedImportableSourceFile(
        callable_name=uri.callable_name, source_file=resolve_uri(uri.source_file, root_path)
    )


@resolve_uri.register
def _resolve_uri_list(uri: list, root_path: os.PathLike = pathlib.Path()) -> typing.List[pathlib.Path]:
    return [resolve_uri(el, root_path) for el in uri]


def resolve_local_uri(
    uri: typing.Union[str, os.PathLike, URI_Node], root_path: os.PathLike
) -> typing.Union[pathlib.Path, URI_Node]:
    if isinstance(uri, os.PathLike) or isinstance(uri, str):
        if isinstance(uri, str):
            try:
                is_path = pathlib.Path(uri).exists()
            except OSError:
                is_path = False
        else:
            is_path = True

        if is_path:
            return pathlib.Path(uri)

    if isinstance(uri, str):
        uri = fields.URI().deserialize(uri)

    assert isinstance(uri, base_nodes.URI), uri
    if not uri.scheme:  # relative path
        if uri.authority or uri.query or uri.fragment:
            raise ValidationError(f"Invalid Path/URI: {uri}")

        local_path_or_remote_uri: typing.Union[pathlib.Path, URI_Node] = pathlib.Path(root_path) / uri.path
    elif uri.scheme == "file":
        if uri.authority or uri.query or uri.fragment:
            raise NotImplementedError(uri)

        local_path_or_remote_uri = pathlib.Path(url2pathname(uri.path))
    elif uri.scheme in ("https", "https"):
        local_path_or_remote_uri = uri
    else:
        raise ValueError(f"Unknown uri scheme {uri.scheme}")

    return local_path_or_remote_uri


def uri_available(uri: URI_Node, root_path: pathlib.Path) -> bool:
    local_path_or_remote_uri = resolve_local_uri(uri, root_path)
    if isinstance(local_path_or_remote_uri, base_nodes.URI):
        response = requests.head(str(local_path_or_remote_uri))
        available = response.status_code == 200
    elif isinstance(local_path_or_remote_uri, pathlib.Path):
        available = local_path_or_remote_uri.exists()
    else:
        raise TypeError(local_path_or_remote_uri)

    return available


def all_uris_available(
    node: typing.Union[GenericNode, list, tuple, dict], root_path: os.PathLike = pathlib.Path()
) -> bool:
    try:
        UriNodeChecker(root_path=root_path).visit(node)
    except FileNotFoundError:
        return False
    else:
        return True


def download_uri_to_local_path(uri: typing.Union[URI_Node, str]) -> pathlib.Path:
    return resolve_uri(uri)


def _download_uri_to_local_path(uri: URI_Node) -> pathlib.Path:
    local_path = BIOIMAGEIO_CACHE_PATH / uri.scheme / uri.authority / uri.path.strip("/") / uri.query
    if local_path.exists():
        warnings.warn(f"found cached {local_path}. Skipping download of {uri}.")
    else:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            urlretrieve(str(uri), str(local_path))
        except Exception:
            logging.getLogger("download").error("Failed to download %s", uri)
            raise

    return local_path


def resolve_raw_resource_description(
    raw_rd: GenericRawRD, root_path: os.PathLike, nodes_module: typing.Any
) -> GenericResolvedNode:
    """resolve all uris and sources"""
    rd = UriNodeTransformer(root_path=root_path).transform(raw_rd)
    rd = SourceNodeTransformer().transform(rd)
    rd = RawNodeTypeTransformer(nodes_module).transform(rd)
    return rd


def is_valid_orcid_id(orcid_id: str):
    """adapted from stdnum.iso7064.mod_11_2.checksum()"""
    check = 0
    for n in orcid_id:
        check = (2 * check + int(10 if n == "X" else n)) % 11
    return check == 1
