import dataclasses
import os
import pathlib
import re
import typing
import zipfile
from io import BytesIO, StringIO

from . import raw_nodes
from .common import DOI_REGEX, yaml

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

        return conflict_free_name

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


def resolve_rdf_source(source: typing.Union[dict, os.PathLike, typing.IO, str, bytes]) -> typing.Tuple[str, dict]:
    # reduce possible source types
    if isinstance(source, (BytesIO, StringIO)):
        source = source.read()
    elif isinstance(source, os.PathLike):
        source = pathlib.Path(source)

    assert isinstance(source, (dict, pathlib.Path, str, bytes))

    if isinstance(source, pathlib.Path):
        source_name = str(source)
    elif isinstance(source, dict):
        source_name = f"{{name: {source.get('name', '<unknown>')}, ...}}"
    elif isinstance(source, (str, bytes)):
        source_name = str(source[:20]) + "..."
    else:
        raise TypeError(source)

    if isinstance(source, str):
        # source might be doi, url or file path -> resolve to pathlib.Path
        if re.fullmatch(DOI_REGEX, source):  # turn doi into url
            import requests
            from urllib.request import urlopen

            zenodo_sandbox_prefix = "10.5072/zenodo."
            if source.startswith(zenodo_sandbox_prefix):
                # zenodo sandbox doi (which is not a valid doi)
                record_id = source[len(zenodo_sandbox_prefix) :]
                response = requests.get(f"https://sandbox.zenodo.org/api/records/{record_id}")
                if not response.ok:
                    raise RuntimeError(response.status_code)

                zenodo_record = response.json()
                rdfs = [f for f in zenodo_record["files"] if f["key"] == "rdf.yaml"]
                assert len(rdfs) == 1
                rdf = rdfs[0]
                source = rdf["links"]["self"]
            else:
                # resolve doi
                # todo: make sure the resolved url points to a rdf.yaml or a zipped package
                response = urlopen(f"https://doi.org/{source}?type=URL")
                source = response.url
                assert isinstance(source, str)
                if not (source.endswith(".yaml") or source.endswith(".zip")):
                    raise NotImplementedError(
                        f"Resolved doi {source_name} to {source}, but don't know where to find 'rdf.yaml' "
                        f"or a packaged resource zip file."
                    )

        assert isinstance(source, str)
        if source.startswith("http"):
            from urllib.request import urlretrieve

            source, resp = urlretrieve(source)
            # todo: check http response code

        try:
            is_path = pathlib.Path(source).exists()
        except OSError:
            is_path = False

        if is_path:
            source = pathlib.Path(source)

    if isinstance(source, (pathlib.Path, str, bytes)):
        # source is either:
        #   - a file path (to a yaml or a packaged zip)
        #   - a yaml string,
        #   - or yaml file or zip package content as bytes

        if yaml is None:
            raise RuntimeError(f"Cannot read RDF from {source_name} without ruamel.yaml dependency!")

        if isinstance(source, bytes):
            potential_package: typing.Union[pathlib.Path, typing.IO, str] = BytesIO(source)
            potential_package.seek(0)  # type: ignore
        else:
            potential_package = source

        if zipfile.is_zipfile(potential_package):
            with zipfile.ZipFile(potential_package) as zf:
                if "rdf.yaml" not in zf.namelist():
                    raise ValueError(f"Package {source_name} does not contain 'rdf.yaml'")

                source = BytesIO(zf.read("rdf.yaml"))

        source = yaml.load(source)

    assert isinstance(source, dict)
    return source_name, source
