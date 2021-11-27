import ast
import dataclasses
import os
import pathlib
import sys
import typing
from urllib.parse import urlparse

import requests

from . import raw_nodes

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

GenericRawNode = typing.TypeVar("GenericRawNode", bound=raw_nodes.RawNode)
GenericRawRD = typing.TypeVar("GenericRawRD", bound=raw_nodes.ResourceDescription)
URI_Type = typing.TypeVar("URI_Type", bound=raw_nodes.URI)


def iter_fields(node: GenericRawNode):
    for field in dataclasses.fields(node):
        yield field.name, getattr(node, field.name)


class NodeVisitor:
    def visit(self, node: typing.Any) -> None:
        method = "visit_" + node.__class__.__name__

        visitor: typing.Callable[[typing.Any], typing.Any] = getattr(self, method, self.generic_visit)

        visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""

        if isinstance(node, raw_nodes.RawNode):
            for field, value in iter_fields(node):
                self.visit(value)
        elif isinstance(node, dict):
            [self.visit(subnode) for subnode in node.values()]
        elif isinstance(node, (tuple, list)):
            [self.visit(subnode) for subnode in node]


class Transformer:
    def transform(self, node: typing.Any) -> typing.Any:
        method = "transform_" + node.__class__.__name__

        transformer: typing.Callable[[typing.Any], typing.Any] = getattr(self, method, self.generic_transformer)

        return transformer(node)

    def generic_transformer(self, node: typing.Any) -> typing.Any:
        return node

    def transform_list(self, node: list) -> list:
        return [self.transform(subnode) for subnode in node]

    def transform_dict(self, node: dict) -> dict:
        return {key: self.transform(value) for key, value in node.items()}


class NodeTransformer(Transformer):
    def generic_transformer(self, node: GenericRawNode) -> GenericRawNode:
        if isinstance(node, raw_nodes.RawNode):
            return dataclasses.replace(node, **{name: self.transform(value) for name, value in iter_fields(node)})
        else:
            return super().generic_transformer(node)


class PathToRemoteUriTransformer(NodeTransformer):
    def __init__(self, *, remote_source: URI_Type):
        remote_path = pathlib.PurePosixPath(remote_source.path).parent.as_posix()
        self.remote_root = dataclasses.replace(remote_source, path=remote_path, uri_string=None)

    def transform_URI(self, node: URI_Type) -> URI_Type:
        if node.scheme == "file":
            assert not node.authority
            assert not node.query
            assert not node.fragment
            return self._transform_Path(pathlib.Path(node.path))

        return node

    def _transform_Path(self, leaf: pathlib.PurePath):
        assert not leaf.is_absolute()
        path = pathlib.PurePosixPath(self.remote_root.path) / leaf
        return dataclasses.replace(self.remote_root, path=path.as_posix(), uri_string=None)

    def transform_PurePath(self, leaf: pathlib.PurePath) -> raw_nodes.URI:
        return self._transform_Path(leaf)

    def transform_PurePosixPath(self, leaf: pathlib.PurePosixPath) -> raw_nodes.URI:
        return self._transform_Path(leaf)

    def transform_PureWindowsPath(self, leaf: pathlib.PureWindowsPath) -> raw_nodes.URI:
        return self._transform_Path(leaf)

    def transform_PosixPath(self, leaf: pathlib.PosixPath) -> raw_nodes.URI:
        return self._transform_Path(leaf)

    def transform_WindowsPath(self, leaf: pathlib.WindowsPath) -> raw_nodes.URI:
        return self._transform_Path(leaf)


def is_valid_orcid_id(orcid_id: str):
    """adapted from stdnum.iso7064.mod_11_2.checksum()"""
    check = 0
    for n in orcid_id:
        check = (2 * check + int(10 if n == "X" else n)) % 11
    return check == 1


class RawNodePackageTransformer(NodeTransformer):
    """Transforms raw node fields specified by <node>._include_in_package to local relative paths.
    Adds remote resources to given dictionary."""

    def __init__(self, remote_resources: typing.Dict[str, typing.Union[pathlib.PurePath, raw_nodes.URI]]):
        super().__init__()
        self.remote_resources = remote_resources

    def _transform_resource(
        self, resource: typing.Union[list, pathlib.PurePath, raw_nodes.URI]
    ) -> typing.Union[typing.List[pathlib.Path], pathlib.Path]:
        if isinstance(resource, list):
            return [self._transform_resource(r) for r in resource]  # type: ignore  # todo: improve annotation
        elif isinstance(resource, pathlib.PurePath):
            name_from = resource
            if resource.is_absolute():
                folder_in_package = ""
            else:
                folder_in_package = resource.parent.as_posix() + "/"
        elif isinstance(resource, raw_nodes.URI):
            name_from = pathlib.PurePath(resource.path)
            folder_in_package = ""
        else:
            raise TypeError(f"Unexpected type {type(resource)} for {resource}")

        stem = name_from.stem
        suffix = name_from.suffix

        conflict_free_name = f"{folder_in_package}{stem}{suffix}"
        for i in range(100000):
            existing_resource = self.remote_resources.get(conflict_free_name)
            if existing_resource is not None and existing_resource != resource:
                conflict_free_name = f"{folder_in_package}{stem}-{i}{suffix}"
            else:
                break
        else:
            raise ValueError(f"Attempting to pack too many resources with name {stem}{suffix}")

        self.remote_resources[conflict_free_name] = resource

        return pathlib.Path(conflict_free_name)

    def generic_transformer(self, node: GenericRawNode) -> GenericRawNode:
        if isinstance(node, raw_nodes.RawNode):
            resolved_data = {
                field.name: self.transform(getattr(node, field.name)) for field in dataclasses.fields(node)
            }
            for incl_field in node._include_in_package:
                resolved_data[incl_field] = self._transform_resource(resolved_data[incl_field])

            return dataclasses.replace(node, **resolved_data)
        else:
            return super().generic_transformer(node)


def _is_path(s: typing.Any) -> bool:
    if not isinstance(s, (str, os.PathLike)):
        return False

    try:
        return pathlib.Path(s).exists()
    except OSError:
        return False


def get_ref_url(type_: Literal["class", "function"], name: str, github_file_url: str) -> str:
    """get github url with line range fragment to reference implementation from non-raw github file url

    example:
    >>> get_ref_url("class", "Binarize", "https://github.com/bioimage-io/core-bioimage-io-python/blob/main/bioimageio/core/prediction_pipeline/_processing.py")
    https://github.com/bioimage-io/core-bioimage-io-python/blob/main/bioimageio/core/prediction_pipeline/_processing.py#L107-L112
    """
    assert not urlparse(github_file_url).fragment, "unexpected url fragment"
    look_for = {"class": ast.ClassDef, "function": ast.FunctionDef}[type_]
    raw_github_file_url = github_file_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    code = requests.get(raw_github_file_url).text
    tree = ast.parse(code)

    for d in tree.body:
        if isinstance(d, look_for):
            assert hasattr(d, "name")
            if d.name == name:  # type: ignore
                assert hasattr(d, "decorator_list")
                start = d.decorator_list[0].lineno if d.decorator_list else d.lineno  # type: ignore
                if sys.version_info >= (3, 8):
                    stop = d.end_lineno
                else:
                    stop = d.lineno + 1
                break
    else:
        raise ValueError(f"{type_} {name} not found in {github_file_url}")

    return f"{github_file_url}#L{start}-L{stop}"


def snake_case_to_camel_case(string: str) -> str:
    return "".join([s.title() for s in string.split("_")])
