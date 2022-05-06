"""simple io functionality to deserialize a resource description from a resource description file (RDF)
(in form of a dict, e.g. from yaml.load('rdf.yaml') to a raw_nodes.ResourceDescription raw node,
which is a python dataclass
"""
import os
import pathlib
import warnings
import zipfile
from hashlib import sha256
from io import StringIO
from tempfile import TemporaryDirectory
from types import ModuleType
from typing import Dict, IO, Optional, Sequence, Tuple, Union

from marshmallow import missing

from bioimageio.spec.shared import RDF_NAMES, raw_nodes, resolve_rdf_source, resolve_rdf_source_and_type, resolve_source
from bioimageio.spec.shared.common import (
    BIOIMAGEIO_CACHE_PATH,
    BIOIMAGEIO_USE_CACHE,
    get_class_name_from_type,
    get_format_version_module,
    get_latest_format_version,
    get_latest_format_version_module,
    no_cache_tmp_list,
    yaml,
)
from bioimageio.spec.shared.node_transformer import (
    AbsoluteToRelativePathTransformer,
    GenericRawNode,
    GenericRawRD,
    RawNodePackageTransformer,
    RelativePathTransformer,
)
from bioimageio.spec.shared.raw_nodes import ResourceDescription as RawResourceDescription
from bioimageio.spec.shared.schema import SharedBioImageIOSchema

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore


LATEST = "latest"


class ConvertersModule(Protocol):
    def maybe_convert(self, data: dict) -> dict:
        raise NotImplementedError


class SubModuleUtils(Protocol):
    def filter_resource_description(self, raw_rd: GenericRawNode, **kwargs) -> GenericRawNode:
        raise NotImplementedError


class SpecSubmodule(Protocol):
    format_version: str

    converters: ConvertersModule
    nodes: ModuleType
    raw_nodes: ModuleType
    schema: ModuleType
    utils: SubModuleUtils


def _get_spec_submodule(type_: str, data_version: str = LATEST) -> SpecSubmodule:
    if not isinstance(data_version, str):
        raise TypeError(f"invalid 'format_version' {data_version}")

    if data_version == LATEST:
        sub_spec = get_latest_format_version_module(type_)
    else:
        sub_spec = get_format_version_module(type_, data_version)

    return sub_spec


def extract_resource_package(
    source: Union[os.PathLike, IO, str, bytes, raw_nodes.URI]
) -> Tuple[dict, str, pathlib.Path]:
    """extract a zip source to BIOIMAGEIO_CACHE_PATH"""
    source, source_name, root = resolve_rdf_source(source)
    if isinstance(root, bytes):
        raise NotImplementedError("package source was bytes")

    if BIOIMAGEIO_USE_CACHE:
        package_path = BIOIMAGEIO_CACHE_PATH / "extracted_packages" / sha256(str(root).encode("utf-8")).hexdigest()
        package_path.mkdir(exist_ok=True, parents=True)
    else:
        tmp_dir = TemporaryDirectory()
        no_cache_tmp_list.append(tmp_dir)
        package_path = pathlib.Path(tmp_dir.name)

    if isinstance(root, raw_nodes.URI):
        for rdf_name in RDF_NAMES:
            if (package_path / rdf_name).exists():
                download = None
                break
        else:
            download = resolve_source(root)

        local_source = download
    else:
        download = None
        local_source = root

    if local_source is not None:
        with zipfile.ZipFile(local_source) as zf:
            zf.extractall(package_path)

    for rdf_name in RDF_NAMES:
        if (package_path / rdf_name).exists():
            break
    else:
        raise FileNotFoundError(f"Missing 'rdf.yaml' in {root} extracted from {download}")

    if download is not None:
        try:
            os.remove(download)
        except Exception as e:
            warnings.warn(f"Could not remove download {download} due to {e}")

    assert isinstance(package_path, pathlib.Path)
    return source, source_name, package_path


def load_raw_resource_description(
    source: Union[dict, os.PathLike, IO, str, bytes, raw_nodes.URI, RawResourceDescription],
    update_to_format: Optional[str] = None,
) -> RawResourceDescription:
    """load a raw python representation from a BioImage.IO resource description.
    Use `bioimageio.core.load_resource_description` for a more convenient representation of the resource.
    and `bioimageio.core.load_raw_resource_description` to ensure the 'root_path' attribute of the returned object is
    a local file path.

    Args:
        source: resource description or resource description file (RDF)
        update_to_format: update resource to specific major.minor format version; ignoring patch version.
    Returns:
        raw BioImage.IO resource
    """
    root = None
    if isinstance(source, RawResourceDescription):
        if update_to_format == "latest":
            update_to_format = get_latest_format_version(source.type)

        if update_to_format is not None and source.format_version != update_to_format:
            # do serialization round-trip to account for 'update_to_format' but keep root_path
            root = source.root_path
            source = serialize_raw_resource_description_to_dict(source)
        else:
            return source

    data, source_name, _root, type_ = resolve_rdf_source_and_type(source)
    if root is None:
        root = _root

    class_name = get_class_name_from_type(type_)

    if update_to_format is None:
        data_version = data.get("format_version", LATEST)
    elif update_to_format == LATEST:
        data_version = LATEST
    else:
        data_version = ".".join(update_to_format.split("."[:2]))
        if update_to_format.count(".") > 1:
            warnings.warn(
                f"Ignoring patch version of update_to_format {update_to_format} "
                f"(always updating to latest patch version)."
            )

    sub_spec = _get_spec_submodule(type_, data_version)
    schema: SharedBioImageIOSchema = getattr(sub_spec.schema, class_name)()

    data = sub_spec.converters.maybe_convert(data)
    raw_rd = schema.load(data)

    if isinstance(root, pathlib.Path):
        root = root.resolve()
        if zipfile.is_zipfile(root):
            # set root to extracted zip package
            _, _, root = extract_resource_package(root)
    elif isinstance(root, bytes):
        root = pathlib.Path().resolve()

    raw_rd.root_path = root
    raw_rd = RelativePathTransformer(root=root).transform(raw_rd)

    return raw_rd


def serialize_raw_resource_description_to_dict(
    raw_rd: RawResourceDescription, convert_absolute_paths: bool = False
) -> dict:
    """serialize a raw nodes resource description to a dict with the content of a resource description file (RDF).
    If 'convert_absolute_paths' all absolute paths are converted to paths relative to raw_rd.root_path before
    serialization.
    """
    class_name = get_class_name_from_type(raw_rd.type)
    sub_spec = _get_spec_submodule(raw_rd.type, raw_rd.format_version)
    schema: SharedBioImageIOSchema = getattr(sub_spec.schema, class_name)()

    if convert_absolute_paths:
        raw_rd = AbsoluteToRelativePathTransformer(root=raw_rd.root_path).transform(raw_rd)

    serialized = schema.dump(raw_rd)
    assert isinstance(serialized, dict)
    assert missing not in serialized.values()

    return serialized


def serialize_raw_resource_description(raw_rd: RawResourceDescription, convert_absolute_paths: bool = True) -> str:
    if yaml is None:
        raise RuntimeError("'serialize_raw_resource_description' requires yaml")

    serialized = serialize_raw_resource_description_to_dict(raw_rd, convert_absolute_paths=convert_absolute_paths)

    with StringIO() as stream:
        yaml.dump(serialized, stream)
        return stream.getvalue()


def save_raw_resource_description(raw_rd: RawResourceDescription, path: pathlib.Path):
    if yaml is None:
        raise RuntimeError("'save_raw_resource_description' requires yaml")

    warnings.warn("only saving serialized rdf, no associated resources.")
    if path.suffix != ".yaml":
        warnings.warn("saving with '.yaml' suffix is strongly encouraged.")

    serialized = serialize_raw_resource_description_to_dict(raw_rd)
    yaml.dump(serialized, path)


def get_resource_package_content_wo_rdf(
    raw_rd: Union[GenericRawRD, raw_nodes.URI, str, pathlib.Path],
    *,
    weights_priority_order: Optional[Sequence[str]] = None,  # model only
) -> Tuple[GenericRawNode, Dict[str, Union[pathlib.PurePath, raw_nodes.URI]]]:
    """
    Args:
        raw_rd: raw resource description
        # for model resources only:
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.

    Returns:
        Tuple of updated raw resource description and package content of remote URIs, local file paths or text content
        keyed by file names.
        Important note: the serialized rdf.yaml is not included.
    """
    if not isinstance(raw_rd, raw_nodes.ResourceDescription):
        raw_rd = load_raw_resource_description(raw_rd)

    sub_spec = _get_spec_submodule(raw_rd.type, raw_rd.format_version)
    if raw_rd.type == "model":
        filter_kwargs = dict(weights_priority_order=weights_priority_order)
    else:
        filter_kwargs = {}

    raw_rd = sub_spec.utils.filter_resource_description(raw_rd, **filter_kwargs)

    content: Dict[str, Union[pathlib.PurePath, raw_nodes.URI, str]] = {}
    raw_rd = RawNodePackageTransformer(content, raw_rd.root_path).transform(raw_rd)
    assert "rdf.yaml" not in content
    return raw_rd, content


def get_resource_package_content(
    raw_rd: Union[GenericRawNode, raw_nodes.URI, str, pathlib.Path],
    *,
    weights_priority_order: Optional[Sequence[str]] = None,  # model only
) -> Dict[str, Union[str, pathlib.PurePath, raw_nodes.URI]]:
    """
    Args:
        raw_rd: raw resource description
        # for model resources only:
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.

    Returns:
        Package content of remote URIs, local file paths or text content keyed by file names.
    """
    if yaml is None:
        raise RuntimeError(
            "'get_resource_package_content' requires yaml; note that 'get_resource_package_content_wo_rdf' may be used "
            "without yaml"
        )

    content: Dict[str, Union[str, pathlib.PurePath, raw_nodes.URI]]
    raw_rd, content = get_resource_package_content_wo_rdf(raw_rd, weights_priority_order=weights_priority_order)
    content["rdf.yaml"] = serialize_raw_resource_description(raw_rd)
    return content
