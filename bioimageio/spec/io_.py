"""simple io functionality to deserialize a resource description from a resource description file (RDF)
(in form of a dict, e.g. from yaml.load('rdf.yaml') to a raw_nodes.ResourceDescription raw node,
which is a python dataclass
"""
import os
import pathlib
import warnings
from io import StringIO
from types import ModuleType
from typing import Any, Dict, Optional, Sequence, Tuple, Union

from bioimageio.spec.shared import raw_nodes
from bioimageio.spec.shared.common import (
    get_class_name_from_type,
    get_format_version_module,
    get_latest_format_version_module,
    yaml,
)
from bioimageio.spec.shared.raw_nodes import ResourceDescription as RawResourceDescription
from bioimageio.spec.shared.schema import SharedBioImageIOSchema
from bioimageio.spec.shared.utils import GenericRawNode, RawNodePackageTransformer

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


def load_raw_resource_description(
    source: Union[Dict[str, Any], os.PathLike, str], update_to_current_format: bool = False
) -> RawResourceDescription:
    """load a raw python representation from a BioImage.IO resource description.
    Use `bioimageio.core.load_raw_resource_description` to load remote resources.
    or  `bioimageio.core.load_resource_description` for a more convenient representation of the resource.

    Args:
        source: resource description or resource description file (RDF)
        update_to_current_format: auto convert content to adhere to the latest appropriate RDF format version

    Returns:
        raw BioImage.IO resource
    """

    if isinstance(source, os.PathLike) or isinstance(source, str):
        source = pathlib.Path(source)
        if yaml is None:
            raise RuntimeError(
                "to load raw resource descriptions from paths, yaml is required. Add ruamel.yaml to your environment "
                "or call `load_raw_resource_description` with a dictionary."
            )

        data: Dict[str, Any] = yaml.load(source)
        root_path = source.parent
    else:
        data = source
        root_path = data.pop("root_path", pathlib.Path())

    type_ = data.get("type", "model")
    class_name = get_class_name_from_type(type_)

    data_version = LATEST if update_to_current_format else data.get("format_version", LATEST)
    sub_spec = _get_spec_submodule(type_, data_version)
    schema: SharedBioImageIOSchema = getattr(sub_spec.schema, class_name)()

    data = sub_spec.converters.maybe_convert(data)
    raw_rd = schema.load(data)
    raw_rd.root_path = root_path
    return raw_rd


def serialize_raw_resource_description_to_dict(raw_rd: RawResourceDescription) -> dict:
    """serialize a raw nodes resource description to a dict with the content of a resource description file (RDF)"""
    class_name = get_class_name_from_type(raw_rd.type)
    sub_spec = _get_spec_submodule(raw_rd.type, raw_rd.format_version)

    schema: SharedBioImageIOSchema = getattr(sub_spec.schema, class_name)()
    serialized = schema.dump(raw_rd)
    assert isinstance(serialized, dict)

    return serialized


def serialize_raw_resource_description(raw_rd: RawResourceDescription) -> str:
    if yaml is None:
        raise RuntimeError("'serialize_raw_resource_description' requires yaml")

    serialized = serialize_raw_resource_description_to_dict(raw_rd)

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
    raw_rd: GenericRawNode, *, weights_priority_order: Optional[Sequence[str]] = None  # model only
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
    assert isinstance(raw_rd, raw_nodes.ResourceDescription)
    sub_spec = _get_spec_submodule(raw_rd.type, raw_rd.format_version)
    if raw_rd.type == "model":
        filter_kwargs = dict(weights_priority_order=weights_priority_order)
    else:
        filter_kwargs = {}

    raw_rd = sub_spec.utils.filter_resource_description(raw_rd, **filter_kwargs)

    content: Dict[str, Union[pathlib.PurePath, raw_nodes.URI, str]] = {}
    raw_rd = RawNodePackageTransformer(content).transform(raw_rd)
    assert "rdf.yaml" not in content
    return raw_rd, content


def get_resource_package_content(
    raw_rd: GenericRawNode, *, weights_priority_order: Optional[Sequence[str]] = None  # model only
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
