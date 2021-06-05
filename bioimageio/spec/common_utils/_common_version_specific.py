import dataclasses
import importlib.util
import logging
import os
import pathlib
import subprocess
import sys
import typing
import uuid
from functools import singledispatch
from urllib.parse import urlunparse
from urllib.request import url2pathname, urlretrieve

from marshmallow import ValidationError, missing

from bioimageio.spec.common_utils.common import Singleton, yaml

BIOIMAGEIO_CACHE_PATH = pathlib.Path(os.getenv("BIOIMAGEIO_CACHE_PATH", pathlib.Path.home() / "bioimageio_cache"))


GenericNode = typing.TypeVar("GenericNode")


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


class CommonVersionSpecificUtils(metaclass=Singleton):
    def __init__(self, version: str):
        self.version = version
        major, minor, patch = map(int, version.split("."))
        if (major, minor) == (0, 3):
            from bioimageio.spec import v0_3 as version_module
        elif (major, minor) == (0, 1):
            from bioimageio.spec import v0_1 as version_module
        else:
            raise NotImplementedError(version)

        self.version_module = version_module
        fields = version_module.fields
        nodes = version_module.nodes
        raw_nodes = version_module.raw_nodes
        schema = version_module.schema

        @dataclasses.dataclass
        class LocalImportableModule(raw_nodes.ImportableModule):
            python_path: pathlib.Path = missing

        class NodeVisitor:
            def visit(self, node: typing.Any) -> None:
                method = "visit_" + node.__class__.__name__

                visitor = getattr(self, method, self.generic_visit)

                visitor(node)

            def generic_visit(self, node):
                """Called if no explicit visitor function exists for a node."""
                if isinstance(node, nodes.Node):
                    for field, value in iter_fields(node):
                        self.visit(value)
                elif isinstance(node, list):
                    [self.visit(subnode) for subnode in node]
                elif isinstance(node, dict):
                    [self.visit(subnode) for subnode in node.values()]
                elif isinstance(node, tuple):
                    assert not any(
                        isinstance(subnode, nodes.Node) or isinstance(subnode, list) or isinstance(subnode, dict)
                        for subnode in node
                    )

        class NodeTransformer(Transformer):
            def generic_transformer(self, node: GenericNode) -> GenericNode:
                if isinstance(node, (nodes.Node, raw_nodes.Node)):
                    return dataclasses.replace(
                        node,
                        **{  # noqa
                            field.name: self.transform(getattr(node, field.name)) for field in dataclasses.fields(node)
                        },
                    )
                else:
                    return super().generic_transformer(node)

        @dataclasses.dataclass
        class ResolvedImportablePath(raw_nodes.ImportablePath):
            pass

        class UriTransformer(Transformer):
            def __init__(self, *, root_path: pathlib.Path):
                self.root_path = root_path

            def _transform_selected_uris(self, uri_key, uri_value):
                """we only want to resolve certain uri's"""
                if uri_key in []:  # todo: "specify keys that point to sub-specs"
                    raise NotImplementedError("cache and substitute sub-spec for uri")

                return uri_key, uri_value

            def transform_dict(self, node: dict) -> dict:
                return {key: value for key, value in map(self._transform_selected_uris, node.keys(), node.values())}

        class UriNodeTransformer(NodeTransformer):
            def __init__(self, *, root_path: pathlib.Path):
                self.root_path = root_path
                self.python_path = self._guess_python_path_from_local_spec_path(root_path=root_path)

            def transform_SpecURI(self, node: raw_nodes.SpecURI) -> typing.Any:
                local_path = resolve_uri(node, root_path=self.root_path)
                data = yaml.load(local_path)

                resolved_node = node.spec_schema.load(data)
                subtransformer = self.__class__(root_path=local_path.parent)
                return subtransformer.transform(resolved_node)

            def transform_URI(self, node: raw_nodes.URI) -> pathlib.Path:
                local_path = resolve_uri(node, root_path=self.root_path)
                return local_path

            def transform_ImportablePath(self, node: raw_nodes.ImportablePath) -> ResolvedImportablePath:
                return ResolvedImportablePath(
                    filepath=(self.root_path / node.filepath).resolve(), callable_name=node.callable_name
                )

            def transform_ImportableModule(self, node: raw_nodes.ImportableModule) -> LocalImportableModule:
                return LocalImportableModule(**dataclasses.asdict(node), python_path=self.python_path)

            def _transform_Path(self, leaf: pathlib.Path):
                assert not leaf.is_absolute()
                return self.root_path / leaf

            def transform_PosixPath(self, leaf: pathlib.PosixPath) -> pathlib.Path:
                return self._transform_Path(leaf)

            def transform_WindowsPath(self, leaf: pathlib.WindowsPath) -> pathlib.Path:
                return self._transform_Path(leaf)

            @staticmethod
            def _guess_python_path_from_local_spec_path(root_path: pathlib.Path):
                def potential_paths():
                    yield root_path
                    yield from root_path.parents

                for path in potential_paths():
                    if (path / "manifest.yaml").exists() or (path / "manifest.yml").exists():
                        return path.resolve()

                return root_path

        class SourceNodeTransformer(NodeTransformer):
            """
            Imports all source callables
            note: Requires previous transformation by _UriNodeTransformer
            """

            class TemporaryInsertionIntoPythonPath:
                def __init__(self, path: str):
                    self.path = path

                def __enter__(self):
                    sys.path.insert(0, self.path)

                def __exit__(self, exc_type, exc_value, traceback):
                    sys.path.remove(self.path)

            def transform_LocalImportableModule(self, node: LocalImportableModule) -> nodes.ImportedSource:
                with self.TemporaryInsertionIntoPythonPath(str(node.python_path)):
                    module = importlib.import_module(node.module_name)

                return nodes.ImportedSource(factory=getattr(module, node.callable_name))

            @staticmethod
            def transform_ImportableModule(node):
                raise RuntimeError(
                    "Encountered raw_nodes.ImportableModule in _SourceNodeTransformer. Apply _UriNodeTransformer first!"
                )

            @staticmethod
            def transform_ResolvedImportablePath(node: ResolvedImportablePath) -> nodes.ImportedSource:
                importlib_spec = importlib.util.spec_from_file_location(
                    f"user_imports.{uuid.uuid4().hex}", node.filepath
                )
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
            def generic_transformer(self, node: GenericRawNode) -> GenericResolvedNode:
                if isinstance(node, raw_nodes.Node):
                    resolved_data = {
                        field.name: self.transform(getattr(node, field.name)) for field in dataclasses.fields(node)
                    }
                    resolved_node_type: typing.Type[GenericResolvedNode] = getattr(nodes, node.__class__.__name__)
                    return resolved_node_type(**resolved_data)
                else:
                    return super().generic_transformer(node)

        def get_instance(node: nodes.Model, **kwargs):
            if isinstance(node, nodes.Model):
                if not isinstance(node.source, nodes.ImportedSource):
                    raise ValueError(
                        f"Encountered unexpected node.source type {type(node.source)}. "
                        f"`get_instance` requires _UriNodeTransformer and _SourceNodeTransformer to be applied beforehand."
                    )

                joined_kwargs = dict(node.kwargs)
                joined_kwargs.update(kwargs)
                return node.source(**joined_kwargs)
            else:
                raise TypeError(node)

        @singledispatch
        def resolve_uri(uri, root_path: pathlib.Path = pathlib.Path()):
            raise TypeError(type(uri))

        @resolve_uri.register
        def _(uri: pathlib.Path, root_path: pathlib.Path = pathlib.Path()) -> pathlib.Path:
            return resolve_uri(fields.URI().deserialize(uri.as_uri()), root_path)

        @resolve_uri.register
        def _(uri: str, root_path: pathlib.Path = pathlib.Path()) -> pathlib.Path:
            return resolve_uri(fields.URI().deserialize(uri), root_path)

        @resolve_uri.register
        def _(uri: raw_nodes.URI, root_path: pathlib.Path) -> pathlib.Path:
            if uri.scheme == "":  # relative path
                if uri.authority or uri.query or uri.fragment:
                    raise ValidationError(f"Invalid Path/URI: {uri}")

                local_path = root_path / uri.path
            elif uri.scheme == "file":
                if uri.authority or uri.query or uri.fragment:
                    raise NotImplementedError(uri)

                local_path = pathlib.Path(url2pathname(uri.path))
            elif uri.authority == "github.com":
                if uri.query:
                    raise ValidationError(f"Invalid github link: {uri}")

                orga, repo_name, blob_releases_archive, commit_id, *in_repo_path = uri.path.strip("/").split("/")
                if blob_releases_archive == "releases":
                    local_path = download_uri_node_to_local_path(uri)
                elif blob_releases_archive == "archive":
                    raise NotImplementedError("unpacking of github archive not implemented")
                    # local_path = download_uri_node_to_local_path(uri)
                elif blob_releases_archive == "blob":
                    in_repo_path = "/".join(in_repo_path)
                    cached_repo_path = BIOIMAGEIO_CACHE_PATH / orga / repo_name / commit_id
                    local_path = cached_repo_path / in_repo_path
                    if not local_path.exists():
                        cached_repo_path = str(cached_repo_path.resolve())
                        subprocess.call(
                            ["git", "clone", f"{uri.scheme}://{uri.authority}/{orga}/{repo_name}.git", cached_repo_path]
                        )
                        # -C <working_dir> available in git 1.8.5+
                        # https://github.com/git/git/blob/5fd09df3937f54c5cfda4f1087f5d99433cce527/Documentation/RelNotes/1.8.5.txt#L115-L116
                        subprocess.call(["git", "-C", cached_repo_path, "checkout", "--force", commit_id])
                else:
                    raise NotImplementedError(f"unkown github url format: {uri} with '{blob_releases_archive}'")
            elif uri.scheme == "https":
                local_path = download_uri_node_to_local_path(uri)
            else:
                raise ValueError(f"Unknown uri scheme {uri.scheme}")

            return local_path

        def download_uri_node_to_local_path(uri_node: raw_nodes.URI) -> pathlib.Path:
            local_path = (
                BIOIMAGEIO_CACHE_PATH / uri_node.scheme / uri_node.authority / uri_node.path.strip("/") / uri_node.query
            )
            if not local_path.exists():
                local_path.parent.mkdir(parents=True, exist_ok=True)
                url_str = urlunparse([uri_node.scheme, uri_node.authority, uri_node.path, "", uri_node.query, ""])
                try:
                    urlretrieve(url_str, str(local_path))
                except Exception:
                    logging.getLogger("download").error("Failed to download %s", uri_node)
                    raise

            return local_path

        def load_model_spec(data: dict, root_path: pathlib.Path) -> raw_nodes.Model:
            # apply raw version_specific_utils
            data: dict = UriTransformer(root_path=root_path).transform(data)

            data: dict = self.version_module.maybe_convert_model(data)  # convert spec to current format
            tree: raw_nodes.Model = schema.Model().load(data)

            return tree

        RawSpec = raw_nodes.Model
        LoadedSpec = typing.NamedTuple("LoadedSpec", raw_spec=RawSpec, root_path=pathlib.Path)
        ResolvedSpec = nodes.Model

        def resolve_all_uris_and_sources(raw_spec: RawSpec, root_path: pathlib.Path) -> ResolvedSpec:
            spec = UriNodeTransformer(root_path=root_path).transform(raw_spec)
            spec = SourceNodeTransformer().transform(spec)
            spec = RawNodeTypeTransformer().transform(spec)
            return spec

        @singledispatch
        def load_spec(uri) -> LoadedSpec:
            raise TypeError(uri)

        @load_spec.register
        def _(uri: str) -> LoadedSpec:
            last_dot = uri.rfind(".")
            second_last_dot = uri[:last_dot].rfind(".")
            spec_suffix = uri[second_last_dot + 1 : last_dot]
            if spec_suffix == "model":
                load_spec_from_data = load_model_spec
            elif spec_suffix in ("transformation", "reader", "sampler"):
                raise NotImplementedError(spec_suffix)
            else:
                raise ValueError(f"Invalid spec suffix: {spec_suffix}")

            local_path = resolve_uri(uri, root_path=BIOIMAGEIO_CACHE_PATH)
            data = yaml.load(local_path)
            root_path = local_path.parent
            return LoadedSpec(load_spec_from_data(data, root_path=root_path), root_path)

        @load_spec.register
        def _(uri: os.PathLike):
            return load_spec(pathlib.Path(uri).absolute().as_uri())

        @singledispatch
        def load_and_resolve_spec(uri) -> ResolvedSpec:
            raise TypeError(uri)

        @load_and_resolve_spec.register
        def _(uri: str) -> ResolvedSpec:
            return resolve_all_uris_and_sources(*load_spec(uri))

        @load_and_resolve_spec.register
        def _(uri: os.PathLike) -> ResolvedSpec:
            return load_and_resolve_spec(pathlib.Path(uri).absolute().as_uri())

        # transformers aka "utils of the utils"; exposed only for testing
        self._NodeTransformer = NodeTransformer
        self._NodeVisitor = NodeVisitor
        self._SourceNodeTransformer = SourceNodeTransformer
        self._UriNodeTransformer = UriNodeTransformer
        self._iter_fields = iter_fields

        # utils  todo: improve names
        self.download_uri_node_to_local_path = download_uri_node_to_local_path
        self.get_instance = get_instance
        self.load_and_resolve_spec = load_and_resolve_spec
        self.load_model_spec = load_model_spec
        self.load_spec = load_spec
