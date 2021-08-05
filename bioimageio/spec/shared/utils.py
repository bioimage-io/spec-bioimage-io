import dataclasses
import pathlib
import typing
from types import ModuleType

from bioimageio.spec.shared import base_nodes, nodes, raw_nodes

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

    def _transform_Path(self, leaf: pathlib.PurePath):
        assert not leaf.is_absolute()
        return self.transform_URI(raw_nodes.URI(path=leaf.as_posix()))

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
    ) -> typing.Union[typing.List[str], str]:
        if isinstance(resource, list):
            return [self._transform_resource(r) for r in resource]
        elif isinstance(resource, pathlib.PurePath):
            name_from = resource
        elif isinstance(resource, raw_nodes.URI):
            name_from = pathlib.PurePath(resource.path)
        else:
            raise TypeError(f"Unexpected type {type(resource)} for {resource}")

        stem = name_from.stem
        suffix = name_from.suffix

        conflict_free_name = f"{stem}{suffix}"
        for i in range(100000):
            if conflict_free_name in self.remote_resources:
                conflict_free_name = f"{stem}-{i}{suffix}"
            else:
                break
        else:
            raise ValueError(f"Attempting to pack too many resources with name {stem}{suffix}")

        self.remote_resources[conflict_free_name] = resource

        return conflict_free_name

    def generic_transformer(self, node: GenericRawNode) -> GenericResolvedNode:
        if isinstance(node, nodes.Node):
            raise NotImplementedError("Packaging resolved nodes is not implemented.")
        elif isinstance(node, raw_nodes.RawNode):
            resolved_data = {
                field.name: self.transform(getattr(node, field.name)) for field in dataclasses.fields(node)
            }
            for incl_field in node._include_in_package:
                resolved_data[incl_field] = self._transform_resource(resolved_data[incl_field])

            return dataclasses.replace(node, **resolved_data)
        else:
            return super().generic_transformer(node)


