"""simple io functionality to deserialize a resource description from a resource description file (RDF)
(in form of a dict, e.g. from yaml.load('rdf.yaml') to a raw_nodes.ResourceDescription raw node,
which is a python dataclass
"""
import os
import pathlib
import re
import warnings
import zipfile
from io import BytesIO, StringIO
from types import ModuleType
from typing import Dict, IO, Optional, Sequence, Tuple, Union

from marshmallow import ValidationError

from bioimageio.spec.shared import raw_nodes
from bioimageio.spec.shared.common import (
    DOI_REGEX,
    get_class_name_from_type,
    get_format_version_module,
    get_latest_format_version_module,
    yaml,
)
from bioimageio.spec.shared.raw_nodes import ResourceDescription as RawResourceDescription
from bioimageio.spec.shared.schema import SharedBioImageIOSchema
from bioimageio.spec.shared.utils import GenericRawNode, GenericRawRD, RawNodePackageTransformer, _is_path

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore


LATEST = "latest"
RDF_NAMES = ("rdf.yaml", "model.yaml")


def resolve_rdf_source(
    source: Union[dict, os.PathLike, IO, str, bytes, raw_nodes.URI]
) -> Tuple[dict, str, Union[pathlib.Path, raw_nodes.URI, bytes]]:
    # reduce possible source types
    if isinstance(source, (BytesIO, StringIO)):
        source = source.read()
    elif isinstance(source, os.PathLike):
        source = pathlib.Path(source)
    elif isinstance(source, raw_nodes.URI):
        source = str(raw_nodes.URI)

    assert isinstance(source, (dict, pathlib.Path, str, bytes)), type(source)

    if isinstance(source, pathlib.Path):
        source_name = str(source)
        root: Union[pathlib.Path, raw_nodes.URI, bytes] = source.parent
    elif isinstance(source, dict):
        source_name = f"{{name: {source.get('name', '<unknown>')}, ...}}"
        root = pathlib.Path()
    elif isinstance(source, (str, bytes)):
        source_name = str(source[:20]) + "..."
        # string might be path or yaml string; for yaml string (or bytes) set root to cwd

        if _is_path(source):
            assert isinstance(source, (str, os.PathLike))
            root = pathlib.Path(source).parent
        else:
            root = pathlib.Path()
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
                for rdf_name in RDF_NAMES:
                    for f in zenodo_record["files"]:
                        if f["key"] == rdf_name:
                            source = f["links"]["self"]
                            break
                    else:
                        continue

                    break
                else:
                    raise ValidationError(f"No RDF found; looked for {RDF_NAMES}")

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

            root = raw_nodes.URI(uri_string=source)
            source, resp = urlretrieve(source)
            # todo: check http response code

        if _is_path(source):
            source = pathlib.Path(source)

    if isinstance(source, (pathlib.Path, str, bytes)):
        # source is either:
        #   - a file path (to a yaml or a packaged zip)
        #   - a yaml string,
        #   - or yaml file or zip package content as bytes

        if yaml is None:
            raise RuntimeError(f"Cannot read RDF from {source_name} without ruamel.yaml dependency!")

        if isinstance(source, bytes):
            potential_package: Union[pathlib.Path, IO, str] = BytesIO(source)
            potential_package.seek(0)  # type: ignore
        else:
            potential_package = source

        if zipfile.is_zipfile(potential_package):
            with zipfile.ZipFile(potential_package) as zf:
                for rdf_name in RDF_NAMES:
                    if rdf_name in zf.namelist():
                        break
                else:
                    raise ValueError(f"Missing 'rdf.yaml' in package {source_name}")

                assert isinstance(source, (pathlib.Path, bytes))
                root = source
                source = BytesIO(zf.read(rdf_name))

        source = yaml.load(source)

    assert isinstance(source, dict)
    return source, source_name, root


def resolve_rdf_source_and_type(
    source: Union[os.PathLike, str, dict, raw_nodes.URI]
) -> Tuple[dict, str, Union[pathlib.Path, raw_nodes.URI, bytes], str]:
    data, source_name, root = resolve_rdf_source(source)

    type_ = data.get("type", "model")  # todo: remove model type default

    return data, source_name, root, type_


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
    source: Union[dict, os.PathLike, IO, str, bytes, raw_nodes.URI, RawResourceDescription],
    update_to_current_format: bool = False,
) -> RawResourceDescription:
    """load a raw python representation from a BioImage.IO resource description.
    Use `bioimageio.core.load_resource_description` for a more convenient representation of the resource.
    and `bioimageio.core.load_raw_resource_description` to ensure the 'root_path' attribute of the returned object is
    a local file path.

    Args:
        source: resource description or resource description file (RDF)
        update_to_current_format: auto convert content to adhere to the latest appropriate RDF format version

    Returns:
        raw BioImage.IO resource
    """
    if isinstance(source, RawResourceDescription):
        return source

    data, source_name, root, type_ = resolve_rdf_source_and_type(source)
    class_name = get_class_name_from_type(type_)

    data_version = LATEST if update_to_current_format else data.get("format_version", LATEST)
    sub_spec = _get_spec_submodule(type_, data_version)
    schema: SharedBioImageIOSchema = getattr(sub_spec.schema, class_name)()

    data = sub_spec.converters.maybe_convert(data)
    raw_rd = schema.load(data)
    raw_rd.root_path = root
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
    raw_rd: GenericRawRD, *, weights_priority_order: Optional[Sequence[str]] = None  # model only
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
    raw_rd = RawNodePackageTransformer(content, raw_rd.root_path).transform(raw_rd)
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
