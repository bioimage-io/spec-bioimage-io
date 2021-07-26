from __future__ import annotations

import os
import pathlib
from typing import Dict, Optional, Sequence, TYPE_CHECKING, Tuple, Union
from zipfile import ZIP_DEFLATED

from bioimageio.spec.shared import raw_nodes
from bioimageio.spec.shared.common import get_format_version_module, get_latest_format_version_module
from bioimageio.spec.shared.io import IO_Interface, Node, RawNode, resolve_rdf_source_and_type

if TYPE_CHECKING:
    import bioimageio.spec.model


def _get_matching_io_class(type_: str, data_version: str = "latest") -> IO_Interface:
    if not isinstance(data_version, str):
        raise TypeError("missing or invalid 'format_version'")

    if data_version == "latest":
        v_mod = get_latest_format_version_module(type_)
    else:
        v_mod = get_format_version_module(type_, data_version)

    return v_mod.utils.IO


def load_raw_node(
    source: Union[os.PathLike, str, dict, raw_nodes.URI], update_to_current_format: bool = False
) -> RawNode:
    """load a raw python representation from a BioImage.IO resource description file (RDF).
    Use `load_node` for a more convenient representation.

    Args:
        source: resource description file (RDF)
        update_to_current_format: auto convert content to adhere to the latest appropriate RDF format version

    Returns:
        raw BioImage.IO resource
    """
    data, type_ = resolve_rdf_source_and_type(source)
    io_cls = _get_matching_io_class(
        type_, "latest" if update_to_current_format else data.get("format_version", "latest")
    )

    if isinstance(source, raw_nodes.URI):
        # not using data here, because a remote source differs from a local source
        return io_cls.load_raw_node(source=source)
    else:
        return io_cls.load_raw_node(source=data)


def serialize_raw_node_to_dict(raw_node: RawNode) -> dict:
    io_cls = _get_matching_io_class(raw_node.type, raw_node.format_version)
    return io_cls.serialize_raw_node_to_dict(raw_node)


def save_raw_node(raw_node: RawNode, path: pathlib.Path):
    io_cls = _get_matching_io_class(raw_node.type, raw_node.format_version)
    return io_cls.save_raw_node(raw_node, path)


def serialize_raw_node(raw_node: Union[dict, RawNode]) -> str:
    if isinstance(raw_node, raw_nodes.Node):
        assert hasattr(raw_node, "type")
        type_ = raw_node.type  # noqa
        assert hasattr(raw_node, "format_version")
        format_version = raw_node.format_version  # noqa
    else:
        assert "type" in raw_node
        type_ = raw_node["type"]
        assert "format_version" in raw_node
        format_version = raw_node["format_version"]

    io_cls = _get_matching_io_class(type_, format_version)
    return io_cls.serialize_raw_node(raw_node)


def ensure_raw_node(
    raw_node: Union[str, dict, os.PathLike, raw_nodes.URI, RawNode],
    root_path: os.PathLike,
    update_to_current_format: bool,
) -> Tuple[RawNode, pathlib.Path]:
    if isinstance(raw_node, raw_nodes.Node) and not isinstance(raw_node, raw_nodes.URI):
        return raw_node, pathlib.Path(root_path)

    data, type_ = resolve_rdf_source_and_type(raw_node)
    format_version = "latest" if update_to_current_format else data.get("format_version", "latest")
    io_cls = _get_matching_io_class(type_, format_version)

    return io_cls.ensure_raw_node(raw_node, root_path)


def load_node(
    source: Union[RawNode, os.PathLike, str, dict, raw_nodes.URI],
    root_path: os.PathLike = pathlib.Path(),
    *,
    update_to_current_format: bool = True,
    weights_priority_order: Optional[Sequence[str]] = None,
) -> Node:
    """load a BioImage.IO resource description file (RDF).
    This includes some transformations for convenience, e.g. importing `source`.
    Use `load_raw_node` to obtain a raw representation instead.

    Args:
        source: resource description file (RDF) or raw BioImage.IO resource
        root_path: to resolve relative paths in the RDF (ignored if source is path/URI)
        update_to_current_format: auto convert content to adhere to the latest appropriate RDF format version
        weights_priority_order: If given only the first weights format present in the model resource is included
    Returns:
        BioImage.IO resource
    """
    raw_node, root_path = ensure_raw_node(source, root_path, update_to_current_format)

    io_cls = _get_matching_io_class(raw_node.type, raw_node.format_version)
    return io_cls.load_node(raw_node, root_path, weights_priority_order=weights_priority_order)


def export_package(
    source: Union[RawNode, os.PathLike, str, dict, raw_nodes.URI],
    root_path: os.PathLike = pathlib.Path(),
    *,
    update_to_current_format: bool = False,
    weights_priority_order: Optional[Sequence[Union[bioimageio.spec.model.raw_nodes.WeightsFormat]]] = None,
    compression: int = ZIP_DEFLATED,
    compression_level: int = 1,
) -> pathlib.Path:
    """Package a BioImage.IO resource as a zip file.

    Args:
        source: raw node, path, URI or raw data as dict
        root_path:  for relative paths (only used if source is RawNode or dict)
        update_to_current_format: Convert not only the patch version, but also the major and minor version.
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.
        compression: The numeric constant of compression method.
        compression_level: Compression level to use when writing files to the archive.
                           See https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile

    Returns:
        path to zipped BioImage.IO package in BIOIMAGEIO_CACHE_PATH.
    """
    raw_node, root_path = ensure_raw_node(source, root_path, update_to_current_format)
    io_cls = _get_matching_io_class(raw_node.type, raw_node.format_version)
    return io_cls.export_package(
        raw_node,
        root_path,
        weights_priority_order=weights_priority_order,
        compression=compression,
        compression_level=compression_level,
    )


def get_package_content(
    source: Union[RawNode, os.PathLike, str, dict],
    root_path: pathlib.Path,
    update_to_current_format: bool = False,
    *,
    weights_priority_order: Optional[Sequence[str]] = None,
) -> Dict[str, Union[str, pathlib.Path]]:
    """
    Args:
        source: raw node, path, URI or raw data as dict
        root_path:  for relative paths (only used if source is RawNode or dict)
        update_to_current_format: Convert not only the patch version, but also the major and minor version.
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.

    Returns:
        Package content of local file paths or text content keyed by file names.
    """
    raw_node, root_path = ensure_raw_node(source, root_path, update_to_current_format)
    io_cls = _get_matching_io_class(raw_node.type, raw_node.format_version)
    return io_cls.get_package_content(raw_node, root_path, weights_priority_order=weights_priority_order)
