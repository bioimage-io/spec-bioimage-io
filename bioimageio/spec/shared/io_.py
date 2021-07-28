# type: ignore  # all sorts of unbound types :)
from __future__ import annotations

import dataclasses
import os
import pathlib
import warnings
from abc import ABC, abstractmethod
from copy import deepcopy
from io import StringIO
from types import ModuleType
from typing import Any, ClassVar, Dict, Optional, Sequence, TYPE_CHECKING, Tuple, TypeVar, Union
from zipfile import ZIP_DEFLATED, ZipFile

from marshmallow import ValidationError, missing

from . import nodes, raw_nodes
from .common import BIOIMAGEIO_CACHE_PATH, NoOverridesDict, Protocol, get_class_name_from_type, yaml
from .raw_nodes import ImportableSourceFile
from .schema import SharedBioImageIOSchema
from .utils import (
    GenericNode,
    PathToRemoteUriTransformer,
    _download_uri_to_local_path,
    resolve_local_uri,
    resolve_raw_node,
    resolve_uri,
)

if TYPE_CHECKING:
    import bioimageio.spec.model


# placeholders for versioned classes
Schema = TypeVar("Schema", bound=SharedBioImageIOSchema)
RawNode = TypeVar("RawNode", bound=raw_nodes.Node)
Node = TypeVar("Node", bound=nodes.Node)


# placeholders for versioned modules
class ConvertersModule(Protocol):
    def maybe_convert(self, data: dict) -> dict:
        raise NotImplementedError


class RawNodesModule(Protocol):
    FormatVersion: Any


class NodesModule(Protocol):
    FormatVersion: Any


# class IO_Meta(ABCMeta):
#     """
#     defines abstract class properties for IO_Interface
#     """
#
#     @property
#     @abstractmethod
#     def preceding_io_class(self) -> IO_Base:
#         raise NotImplementedError


# IO interface to clarify intention of IO classes
# class IO_Interface(metaclass=IO_Meta):
class IO_Interface(ABC):
    """
    each bioimageio.spec type submodule has submodules for released minor format versions to validate and work with
    previously released format versions. Each version submodule implements its own IO class. The IO_Base class is used
    to share generic io code across types and versions (see below).
    """

    # modules with format version specific implementations of schema, nodes, etc.
    # todo: 'real' abstract class properties for IO_Interface. see IO_Meta draft above
    preceding_io_class: ClassVar[Optional[IO_Base]]
    converters: ClassVar[ConvertersModule]
    schema: ClassVar[ModuleType]
    raw_nodes: ClassVar[RawNodesModule]
    nodes: ClassVar[NodesModule]

    # RDF -> raw node
    @classmethod
    @abstractmethod
    def load_raw_node(cls, source: Union[os.PathLike, str, dict, raw_nodes.URI]) -> RawNode:
        """load a raw python representation from a BioImage.IO resource description file (RDF).
        Use `load_node` for a more convenient representation.

        Args:
            source: resource description file (RDF)

        Returns:
            raw BioImage.IO resource
        """
        raise NotImplementedError

    @classmethod
    def ensure_raw_node(cls, raw_node: Union[str, dict, os.PathLike, raw_nodes.URI, RawNode], root_path: os.PathLike):
        raise NotImplementedError

    @classmethod
    def maybe_convert(cls, data: dict):
        """If resource 'data' is specified in a preceding format, convert it to the (newer) format of this IO class.

        Args:
            data: raw RDF data as loaded by yaml
        """
        raise NotImplementedError

    # raw node -> RDF
    @classmethod
    def serialize_raw_node_to_dict(cls, raw_node: RawNode) -> dict:
        """Serialize a `raw_nodes.<Model|Collection|...>` object with marshmallow to a plain dict with only basic data types"""
        raise NotImplementedError

    @classmethod
    def serialize_raw_node(cls, raw_node: Union[dict, RawNode]) -> str:
        """Serialize a raw model to a yaml string"""
        raise NotImplementedError

    @classmethod
    def save_raw_node(cls, raw_node: RawNode, path: pathlib.Path) -> None:
        """Serialize a raw model to a new yaml file at 'path'"""
        raise NotImplementedError

    # RDF|raw node -> (evaluated) node
    @classmethod
    def load_node(
        cls,
        source: Union[RawNode, os.PathLike, str, dict, raw_nodes.URI],
        root_path: os.PathLike = pathlib.Path(),
        *,
        weights_priority_order: Optional[Sequence[str]] = None,
    ) -> Node:
        """load a BioImage.IO resource description file (RDF).
        This includes some transformations for convenience, e.g. importing `source`.
        Use `load_raw_node` to obtain a raw representation instead.

        Args:
            source: resource description file (RDF) or raw BioImage.IO resource
            root_path: to resolve relative paths in the RDF (ignored if source is path/URI)
            weights_priority_order: If given only the first weights format present in the model resource is included
        Returns:
            BioImage.IO resource
        """
        raise NotImplementedError

    # RDF|raw node -> package
    @classmethod
    def get_package_content(
        cls,
        source: Union[RawNode, os.PathLike, str, dict],
        root_path: pathlib.Path,
        update_to_current_format: bool = False,
        weights_priority_order: Optional[Sequence[str]] = None,
    ) -> Dict[str, Union[str, pathlib.Path]]:
        """Gather content required for exporting a bioimage.io package from an RDF source.

        Args:
            source: raw node, path, URI or raw data as dict
            root_path:  for relative paths (only used if source is RawNode or dict)
            update_to_current_format: Convert not only the patch version, but also the major and minor version.
            weights_priority_order: If given only the first weights format present in the model is included.
                                    If none of the prioritized weights formats is found all are included.

        Returns:
            Package content of local file paths or text content keyed by file names.
        """
        raise NotImplementedError

    @classmethod
    def export_package(
        cls,
        source: Union[RawNode, os.PathLike, str, dict, raw_nodes.URI],
        root_path: os.PathLike = pathlib.Path(),
        *,
        output_path: Optional[os.PathLike] = None,
        weights_priority_order: Optional[Sequence[bioimageio.spec.model.raw_nodes.WeightsFormat]] = None,
        compression: int = ZIP_DEFLATED,
        compression_level: int = 1,
    ) -> pathlib.Path:
        """Package a BioImage.IO resource as a zip file.

        Args:
            source: raw node, path, URI or raw data as dict
            root_path:  for relative paths (only used if source is RawNode or dict)
            output_path: file path to write package to
            weights_priority_order: If given only the first weights format present in the model is included.
                                    If none of the prioritized weights formats is found all are included.
            compression: The numeric constant of compression method.
            compression_level: Compression level to use when writing files to the archive.
                               See https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile

        Returns:
            path to zipped BioImage.IO package in BIOIMAGEIO_CACHE_PATH.
        """
        raise NotImplementedError


class IO_Base(IO_Interface):
    @classmethod
    def load_raw_node(cls, source: Union[os.PathLike, str, dict, raw_nodes.URI]) -> RawNode:
        data, type_ = resolve_rdf_source_and_type(source)
        data = cls.maybe_convert(data)

        schema_class_name = get_class_name_from_type(type_)
        schema_class = getattr(cls.schema, schema_class_name)
        if schema_class is None:
            raise ValueError(f"not a valid schema: {type_.title()}")

        raw_node_class = getattr(cls.raw_nodes, type_.title())
        if raw_node_class is None:
            raise NotImplementedError(f"missing implementation of raw node: {type_.title()}")

        raw_node = schema_class().load(data)
        assert isinstance(raw_node, raw_node_class)

        if isinstance(source, raw_nodes.URI) or isinstance(source, str) and source.startswith("http"):
            # for a remote source relative paths are invalid; replace all relative file paths in source with URLs
            if isinstance(source, str):
                source = raw_nodes.URI(source)

            warnings.warn(
                f"changing file paths in RDF to URIs due to a remote {source.scheme} source "
                "(may result in an invalid node)"
            )
            raw_node = PathToRemoteUriTransformer(remote_source=source).transform(raw_node)

        assert isinstance(raw_node, raw_node_class)
        return raw_node

    @classmethod
    def serialize_raw_node_to_dict(cls, raw_node: RawNode) -> dict:
        schema_class_name = get_class_name_from_type(raw_node.type)
        schema_class = getattr(cls.schema, schema_class_name)
        if schema_class is None:
            raise NotImplementedError(f"{schema_class_name} schema")

        serialized = schema_class().dump(raw_node)
        assert isinstance(serialized, dict)
        return serialized

    @classmethod
    def save_raw_node(cls, raw_node: RawNode, path: pathlib.Path):
        warnings.warn("only saving serialized rdf, no associated resources.")
        if path.suffix != ".yaml":
            warnings.warn("saving with '.yaml' suffix is strongly encouraged.")

        serialized = cls.serialize_raw_node_to_dict(raw_node)
        yaml.dump(serialized, path)

    @classmethod
    def serialize_raw_node(cls, raw_node: Union[dict, RawNode]) -> str:
        if not isinstance(raw_node, dict):
            raw_node = cls.serialize_raw_node_to_dict(raw_node)

        with StringIO() as stream:
            yaml.dump(raw_node, stream)
            return stream.getvalue()

    @classmethod
    def ensure_raw_node(cls, raw_node: Union[str, dict, os.PathLike, raw_nodes.URI, RawNode], root_path: os.PathLike):
        if isinstance(raw_node, raw_nodes.Node):
            return raw_node, root_path
        elif isinstance(raw_node, dict):
            pass
        elif isinstance(raw_node, (str, os.PathLike, raw_nodes.URI)):
            local_raw_node = resolve_uri(raw_node, root_path)
            if local_raw_node.suffix == ".zip":
                local_raw_node = extract_zip(local_raw_node)
                raw_node = local_raw_node  # zip package contains everything. ok to 'forget' that source was remote

            root_path = local_raw_node.parent
        else:
            raise TypeError(raw_node)

        return cls.load_raw_node(raw_node), root_path

    @classmethod
    def maybe_convert(cls, data: dict):
        if cls.preceding_io_class is not None:
            data = cls.preceding_io_class.maybe_convert(data)

        return cls.converters.maybe_convert(data)

    @classmethod
    def load_node(
        cls,
        source: Union[RawNode, os.PathLike, str, dict, raw_nodes.URI],
        root_path: os.PathLike = pathlib.Path(),
        *,
        weights_priority_order: Optional[Sequence[str]] = None,
    ):
        raw_node, root_path = cls.ensure_raw_node(source, root_path)

        if weights_priority_order is not None:
            for wf in weights_priority_order:
                if wf in raw_node.weights:
                    raw_node.weights = {wf: raw_node.weights[wf]}
                    break
            else:
                raise ValueError(f"Not found any of the specified weights formats ({weights_priority_order})")

        node: Node = resolve_raw_node(raw_node=raw_node, root_path=pathlib.Path(root_path), nodes_module=cls.nodes)
        assert isinstance(node, cls.nodes.Model)

        return node

    @classmethod
    def export_package(
        cls,
        source: Union[RawNode, os.PathLike, str, dict, raw_nodes.URI],
        root_path: os.PathLike = pathlib.Path(),
        *,
        output_path: Optional[os.PathLike] = None,
        weights_priority_order: Optional[Sequence[bioimageio.spec.model.raw_nodes.WeightsFormat]] = None,
        compression: int = ZIP_DEFLATED,
        compression_level: int = 1,
    ) -> pathlib.Path:
        raw_node, root_path = cls.ensure_raw_node(source, root_path)

        if output_path is None:
            package_path = cls._get_tmp_package_path(raw_node, weights_priority_order)
        else:
            package_path = output_path

        package_content = cls.get_package_content(
            raw_node, root_path=root_path, weights_priority_order=weights_priority_order
        )
        make_zip(package_path, package_content, compression=compression, compression_level=compression_level)
        return package_path

    @staticmethod
    def _get_tmp_package_path(
        raw_node: RawNode, weights_priority_order: Optional[Sequence[bioimageio.spec.model.raw_nodes.WeightsFormat]]
    ):
        package_file_name = raw_node.name
        if raw_node.version is not missing:
            package_file_name += f"_{raw_node.version}"

        if weights_priority_order is not None:
            # add weights format to package file name
            for wf in weights_priority_order:
                if wf in raw_node.weights:
                    package_file_name += f"_{wf}"
                    break
            else:
                raise ValueError(
                    f"None of the requested weights ({weights_priority_order}) "
                    f"found in model weights ({raw_node.weights.keys()})"
                )

        package_file_name = package_file_name.replace(" ", "_").replace(".", "_")

        BIOIMAGEIO_CACHE_PATH.mkdir(exist_ok=True, parents=True)
        package_path = (BIOIMAGEIO_CACHE_PATH / package_file_name).with_suffix(".zip")
        max_cached_packages_with_same_name = 100
        for p in range(max_cached_packages_with_same_name):
            if package_path.exists():
                package_path = (BIOIMAGEIO_CACHE_PATH / f"{package_file_name}p{p}").with_suffix(".zip")
            else:
                break
        else:
            raise FileExistsError(
                f"Already caching {max_cached_packages_with_same_name} versions of {BIOIMAGEIO_CACHE_PATH / package_file_name}!"
            )

        return package_path

    @classmethod
    def get_package_content(
        cls,
        source: Union[RawNode, os.PathLike, str, dict],
        root_path: pathlib.Path,
        update_to_current_format: bool = False,
        weights_priority_order: Optional[Sequence[str]] = None,
    ) -> Dict[str, Union[str, pathlib.Path]]:
        raw_node, root_path = cls.ensure_raw_node(source, root_path)
        assert isinstance(raw_node, cls.raw_nodes.Model)

        raw_node = deepcopy(raw_node)

        package = NoOverridesDict(
            key_exists_error_msg="Package content conflict for {key}"
        )  # todo: add check in model validation
        package["original_rdf.txt"] = cls.serialize_raw_node(raw_node)
        # todo: .txt -> .yaml once 'rdf.yaml' is only valid rdf file name in package

        def incl_as_local(node: GenericNode, field_name: str) -> GenericNode:
            value = getattr(node, field_name)
            if value is not missing:
                if isinstance(value, list):
                    fps = [resolve_uri(v, root_path=root_path) for v in value]
                    for fp in fps:
                        package[fp.name] = fp

                    new_field_value = [pathlib.Path(fp.name) for fp in fps]
                else:
                    fp = resolve_uri(value, root_path=root_path)
                    package[fp.name] = fp
                    new_field_value = pathlib.Path(fp.name)

                node = dataclasses.replace(node, **{field_name: new_field_value})

            return node

        raw_node = incl_as_local(raw_node, "documentation")
        raw_node = incl_as_local(raw_node, "test_inputs")
        raw_node = incl_as_local(raw_node, "test_outputs")
        raw_node = incl_as_local(raw_node, "covers")

        # todo: improve dependency handling
        if raw_node.dependencies is not missing:
            dep = incl_as_local(raw_node.dependencies, "file")
            raw_node = dataclasses.replace(raw_node, dependencies=dep)

        if isinstance(raw_node.source, ImportableSourceFile):
            source = incl_as_local(raw_node.source, "source_file")
            raw_node = dataclasses.replace(raw_node, source=source)

        # filter weights
        for wfp in weights_priority_order or []:
            if wfp in raw_node.weights:
                weights = {wfp: raw_node.weights[wfp]}
                break
        else:
            weights = raw_node.weights

        # add weights
        local_weights = {}
        for wf, weights_entry in weights.items():
            weights_entry = incl_as_local(weights_entry, "source")
            local_files = []
            if weights_entry.attachments is not missing:
                for fa in weights_entry.attachments.get("files", []):
                    fa = resolve_uri(fa, root_path=root_path)
                    package[fa.name] = fa
                    local_files.append(fa.name)

            if local_files:
                weights_entry.attachments["files"] = local_files

            local_weights[wf] = weights_entry

        raw_node = dataclasses.replace(raw_node, weights=local_weights)

        # attachments:files
        if raw_node.attachments is not missing:
            local_files = []
            for fa in raw_node.attachments.get("files", []):
                fa = resolve_uri(fa, root_path=root_path)
                package[fa.name] = fa
                local_files.append(fa.name)

            if local_files:
                raw_node.attachments["files"] = local_files

        package["rdf.yaml"] = cls.serialize_raw_node(raw_node)
        return dict(package)


def extract_zip(source: Union[os.PathLike, str, raw_nodes.URI]) -> pathlib.Path:
    """extract a zip source to BIOIMAGEIO_CACHE_PATH"""
    local_source = resolve_uri(source)
    assert isinstance(local_source, pathlib.Path)
    BIOIMAGEIO_CACHE_PATH.mkdir(exist_ok=True, parents=True)
    package_path = BIOIMAGEIO_CACHE_PATH / f"{local_source.stem}_unzipped"
    with ZipFile(local_source) as zf:
        zf.extractall(package_path)

    for rdf_name in ["rdf.yaml", "model.yaml", "rdf.yml", "model.yml"]:
        rdf_path = package_path / rdf_name
        if rdf_path.exists():
            break
    else:
        raise FileNotFoundError(local_source / "rdf.yaml")

    return rdf_path


def make_zip(
    path: os.PathLike, content: Dict[str, Union[str, pathlib.Path]], *, compression: int, compression_level: int
) -> None:
    """Write a zip archive.

    Args:
        path: output path to write to.
        content: dict with archive names and local file paths or strings for text files.
        compression: The numeric constant of compression method.
        compression_level: Compression level to use when writing files to the archive.
                           See https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile

    """
    with ZipFile(path, "w", compression=compression, compresslevel=compression_level) as myzip:
        for arc_name, file_or_str_content in content.items():
            if isinstance(file_or_str_content, str):
                myzip.writestr(arc_name, file_or_str_content)
            else:
                myzip.write(file_or_str_content, arcname=arc_name)


def resolve_rdf_source_and_type(source: Union[os.PathLike, str, dict, raw_nodes.URI]) -> Tuple[dict, str]:
    if isinstance(source, dict):
        data = source
    else:
        source = resolve_local_uri(source, pathlib.Path())
        data, root_path = get_dict_and_root_path_from_yaml_source(source)

    type_ = data.get("type", "model")  # todo: remove default 'model' type

    return data, type_


def get_dict_and_root_path_from_yaml_source(
    source: Union[os.PathLike, str, raw_nodes.URI, dict]
) -> Tuple[dict, pathlib.Path]:
    if isinstance(source, dict):
        return source, pathlib.Path()
    elif isinstance(source, (str, os.PathLike, raw_nodes.URI)):
        source = resolve_local_uri(source, pathlib.Path())
    else:
        raise TypeError(source)

    if isinstance(source, raw_nodes.URI):  # remote uri
        local_source = _download_uri_to_local_path(source)
        root_path = pathlib.Path()
    else:
        local_source = source
        root_path = source.parent

    assert isinstance(local_source, pathlib.Path)
    if local_source.suffix == ".zip":
        local_source = extract_zip(local_source)

    if local_source.suffix == ".yml":
        warnings.warn(
            "suffix '.yml' is not recommended and will raise a ValidationError in the future. Use '.yaml' instead "
            "(https://yaml.org/faq.html)"
        )
    elif local_source.suffix != ".yaml":
        raise ValidationError(f"invalid suffix {local_source.suffix} for source {source}")

    data = yaml.load(local_source)
    assert isinstance(data, dict)
    return data, root_path
