import dataclasses
from importlib.resources import Resource
import os
import traceback
from urllib.parse import urljoin, urlparse
import warnings
from pathlib import Path, PurePath
from typing import (
    Any,
    Callable,
    Dict,
    IO,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
)
from typing_extensions import LiteralString
from pydantic import AnyUrl, HttpUrl, TypeAdapter
import pydantic
from bioimageio.spec import __version__
from bioimageio.spec._internal._constants import IN_PACKAGE_MESSAGE
from bioimageio.spec._internal._utils import nest_dict, nest_dict_with_narrow_first_key
from bioimageio.spec.shared.nodes import FrozenDictNode, Node
from bioimageio.spec.shared.types import FileSource, Loc, RawMapping, RelativeFilePath
from bioimageio.spec.shared.validation import (
    LegacyValidationSummary,
    ValidationContext,
    ValidationSummary,
    ValidationError,
    ValidationWarning,
)

from bioimageio.spec import (
    LatestResourceDescription,
    ResourceDescription,
    generic,
    application,
    collection,
    model,
    dataset,
    notebook,
    __version__,
)
from bioimageio.spec._internal._warn import WarningType, WARNING_LEVEL_CONTEXT_KEY, WarningLevel

# from .collection.v0_2 import default_enrich_partial_rdf, resolve_collection_entries
# from .io_ import (
#     load_raw_resource_description,
#     resolve_rdf_source,
#     save_raw_resource_description,
#     serialize_raw_resource_description_to_dict,
# )
# from .shared import update_nested
# from .shared.common import ValidationSummary, ValidationWarning, nested_default_dict_as_nested_dict, yaml
# from .shared.raw_nodes import ResourceDescription as RawResourceDescription, URI
# from .v import __version__

LATEST: Literal["latest"] = "latest"


def get_rd_class(type_: str, /, format_version: str = LATEST) -> Type[ResourceDescription]:
    assert isinstance(format_version, str)
    if format_version.count(".") == 0:
        format_version = format_version + ".0"
    elif format_version.count(".") == 2:
        format_version = format_version[: format_version.rfind(".")]

    spec = (
        dict(
            model={LATEST: model.Model, "0.4": model.v0_4.Model},
            application={LATEST: application.Application, "0.2": application.v0_2.Application},
            collection={LATEST: collection.Collection, "0.2": collection.v0_2.Collection},
            dataset={LATEST: dataset.Dataset, "0.2": dataset.v0_2.Dataset},
            notebook={LATEST: notebook.Notebook, "0.2": notebook.v0_2.Notebook},
        )
        .get(type_, {LATEST: generic.Generic, "0.2": generic.v0_2.Generic})
        .get(format_version)
    )
    if spec is None:
        raise NotImplementedError(f"{type_} spec {format_version} does not exist.")

    return spec


def update_format(
    resource_description: RawMapping,
    update_to_format: str = "latest",
) -> RawMapping:
    """Auto-update fields of a bioimage.io resource without any validation"""
    assert "type" in resource_description
    assert isinstance(resource_description["type"], str)
    rd_class = get_rd_class(resource_description["type"], update_to_format)
    rd = dict(resource_description)
    rd_class.convert_from_older_format(rd)
    return rd


RD = TypeVar("RD", bound=ResourceDescription)


def _load_descr_impl(adapter: TypeAdapter[RD], resource_description: RawMapping, context: ValidationContext):
    rd: Optional[RD] = None
    error: Union[List[ValidationError], str, None] = None
    val_warnings: List[ValidationWarning] = []
    tb: Optional[List[str]] = None
    try:
        rd = adapter.validate_python(resource_description, context=dataclasses.asdict(context))
    except pydantic.ValidationError as e:
        val_errors: List[ValidationError] = []
        for ee in e.errors(include_url=False):
            if (type_ := ee["type"]) in get_args(WarningType):
                val_warnings.append(ValidationWarning(loc=ee["loc"], msg=ee["msg"], type=type_))  # type: ignore
            else:
                val_errors.append(ValidationError(loc=ee["loc"], msg=ee["msg"], type=ee["type"]))

        error = val_errors or None
    except Exception as e:
        error = str(e)
        assert error
        tb = traceback.format_tb(e.__traceback__)

    return rd, error, tb, val_warnings


def _load_description_from_adapter(
    adapter: TypeAdapter[RD], resource_description: RawMapping, context: ValidationContext
) -> Tuple[Optional[RD], ValidationSummary]:
    rd, error, tb, val_warnings = _load_descr_impl(
        adapter, resource_description, dataclasses.replace(context, **{WARNING_LEVEL_CONTEXT_KEY: 50})
    )  # ignore any warnings using warning level 50 ('ERROR'/'CRITICAL') on first loading attempt
    if rd is None:
        resource_type = resource_description.get("type", "unknown")
        format_version = resource_description.get("format_version", "?.?.?")
    else:
        resource_type = rd.type
        format_version = rd.format_version
        assert error is None, "got rd, but also an error"
        assert tb is None, "got rd, but also an error traceback"
        assert not val_warnings, "got rd, but also already warnings"
        _, error2, tb2, val_warnings = _load_descr_impl(
            adapter, resource_description, context
        )  # may not return rd due to raised warnings
        assert error2 is None, "increasing warning level caused errors"
        assert tb2 is None, "increasing warning level lead to error traceback"

    summary = ValidationSummary(
        bioimageio_spec_version=__version__,
        error=error,
        name=f"bioimageio.spec static {resource_type} validation (format version: {format_version}).",
        source_name=(context.root / "rdf.yaml").as_posix()
        if isinstance(context.root, PurePath)
        else urljoin(str(context.root), "rdf.yaml"),
        status="passed" if error is None else "failed",
    )
    if tb:
        summary["traceback"] = tb

    if val_warnings:
        summary["warnings"] = val_warnings

    return rd, summary


def load_description_as_latest(
    resource_description: RawMapping,  # raw resource description (e.g. loaded from an rdf.yaml file).
    context: ValidationContext = ValidationContext(),
) -> Tuple[LatestResourceDescription, ValidationSummary]:
    """load a resource description in the latest available format.

    If `root` is a path, relative file paths are checked for existence"""

    return _load_description_from_adapter(TypeAdapter(LatestResourceDescription), resource_description, context)


def load_description(
    resource_description: RawMapping,  # raw resource description (e.g. loaded from an rdf.yaml file).
    context: ValidationContext = ValidationContext(),
) -> Tuple[ResourceDescription, ValidationSummary]:
    """Validate a bioimage.io resource description, i.e. the content of a resource description file (RDF)."""

    return _load_description_from_adapter(TypeAdapter(ResourceDescription), resource_description, context)


def validate(
    resource_description: RawMapping,  # raw resource description (e.g. loaded from an rdf.yaml file).
    context: ValidationContext = ValidationContext(),
    update_format: bool = False,  # apply auto-conversion to the latest type-specific format before validating.
) -> ValidationSummary:
    if update_format:
        out = load_description_as_latest(resource_description, context)
    else:
        out = load_description(resource_description, context)

    if isinstance(out, ValidationSummary):
        return out
    else:
        assert len(out._validation_summaries) == 1
        return out._validation_summaries[0]


def validate_legacy(
    resource_description: RawMapping,  # raw resource description (e.g. loaded from an rdf.yaml file).
    context: ValidationContext = ValidationContext(),
    update_format: bool = False,  # apply auto-conversion to the latest type-specific format before validating.
) -> LegacyValidationSummary:
    """Validate a bioimage.io resource description returning the legacy validaiton summary.

    The legacy validation summary contains any errors and warnings as nested dict."""

    vs = validate(resource_description, context, update_format)

    error = vs["error"]
    legacy_error = (
        error if (error is None or isinstance(error, str)) else nest_dict({e["loc"]: e["msg"] for e in error})
    )
    tb = vs.get("traceback")
    return LegacyValidationSummary(
        bioimageio_spec_version=vs["bioimageio_spec_version"],
        error=legacy_error,
        name=vs["name"],
        source_name=vs["source_name"],
        status=vs["status"],
        traceback=None if tb is None else list(tb),
        warnings=nest_dict({w["loc"]: w["msg"] for w in vs["warnings"]}) if "warnings" in vs else {},
    )


def prepare_to_package(
    rd: ResourceDescription,
    *,
    weights_priority_order: Optional[Sequence[str]] = None,  # model only
) -> Tuple[ResourceDescription, Dict[str, Union[HttpUrl, Path]]]:
    """
    Args:
        rd: resource description
        # for model resources only:
        weights_priority_order: If given, only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found a ValueError is raised.

    Returns:
        Modified resource description copy and associated package content mapping file names to URLs or local paths,
        which are referenced in the modfieid resource description.
        Important note: The serialized resource description itself (= an rdf.yaml file) is not included.
    """
    if weights_priority_order is not None and isinstance(rd, model.AnyModel):
        # select single weights entry
        for w in weights_priority_order:
            weights_entry = rd.weights.get(w)
            if weights_entry is not None:
                rd = rd.model_copy(update=dict(weights={w: weights_entry}))
                break
        else:
            raise ValueError("None of the weight formats in `weights_priority_order` is present in the given model.")

    package_content: Dict[Loc, Union[HttpUrl, Path]] = {}
    _fill_resource_package_content(package_content, rd, node_loc=())
    file_names: Dict[Loc, str] = {}
    file_sources: Dict[str, Union[HttpUrl, Path]] = {}
    for loc, src in package_content.items():
        file_name = _extract_file_name(src)
        if file_name in file_sources and file_sources[file_name] != src:
            for i in range(2, 10):
                fn, *ext = file_name.split(".")
                alternative_file_name = ".".join([f"{fn}_{i}", *ext])
                if alternative_file_name not in file_sources or file_sources[alternative_file_name] == src:
                    file_name = alternative_file_name
                    break
            else:
                raise RuntimeError(f"Too many file name clashes for {file_name}")

        file_sources[file_name] = src
        file_names[loc] = file_name

    # update resource description to point to local files
    rd = rd.model_copy(update=nest_dict_with_narrow_first_key(file_names, str))

    return rd, file_sources


def _extract_file_name(src: Union[HttpUrl, PurePath]) -> str:
    if isinstance(src, PurePath):
        return src.name
    else:
        return urlparse(str(src)).path.split("/")[-1]


def _fill_resource_package_content(
    package_content: Dict[Loc, Union[HttpUrl, Path]],
    node: Node,
    node_loc: Loc,
):
    field_value: Union[Tuple[Any, ...], Node, Any]
    for field_name, field_value in node:
        loc = node_loc + (field_name,)
        # nested node
        if isinstance(field_value, Node):
            if not isinstance(field_value, FrozenDictNode):
                _fill_resource_package_content(package_content, field_value, loc)

        # nested node in tuple
        elif isinstance(field_value, tuple):
            for i, fv in enumerate(field_value):
                if isinstance(fv, Node) and not isinstance(fv, FrozenDictNode):
                    _fill_resource_package_content(package_content, fv, loc + (i,))

        elif (node.model_fields[field_name].description or "").startswith(IN_PACKAGE_MESSAGE):
            if isinstance(field_value, RelativeFilePath):
                src = field_value.absolute
            elif isinstance(field_value, AnyUrl):
                src = field_value
            else:
                raise NotImplementedError(f"Package field of type {type(field_value)} not implemented.")

            package_content[loc] = src


def load_raw_resource_description(
    source: Union[dict, os.PathLike, IO, str, bytes, raw_nodes.URI, RawResourceDescription],
    update_to_format: Optional[str] = None,
) -> RawResourceDescription:
    """load a raw python representation from a bioimage.io resource description.
    Use `bioimageio.core.load_resource_description` for a more convenient representation of the resource.
    and `bioimageio.core.load_raw_resource_description` to ensure the 'root_path' attribute of the returned object is
    a local file path.

    Args:
        source: resource description or resource description file (RDF)
        update_to_format: update resource to specific major.minor format version; ignoring patch version.
    Returns:
        raw bioimage.io resource
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

    # determine submodule's format version
    original_data_version = data.get("format_version")
    if original_data_version is None:
        odv: Optional[Version] = None
    else:
        try:
            odv = Version(original_data_version)
        except Exception as e:
            raise ValueError(f"Invalid format version {original_data_version}.") from e

    if update_to_format is None:
        data_version = original_data_version or LATEST
    elif update_to_format == LATEST:
        data_version = LATEST
    else:
        data_version = ".".join(update_to_format.split("."[:2]))
        if update_to_format.count(".") > 1:
            warnings.warn(
                f"Ignoring patch version of update_to_format {update_to_format} "
                f"(always updating to latest patch version)."
            )

    try:
        sub_spec = _get_spec_submodule(type_, data_version)
    except ValueError as e:
        if odv is None:
            raise e  # raise original error; no second attempt with 'LATEST' format version

        try:
            # load latest spec submodule
            sub_spec = _get_spec_submodule(type_, data_version=LATEST)
        except ValueError:
            raise e  # raise original error with desired data_version

        if odv <= Version(sub_spec.format_version):
            # original format version is not a future version.
            # => we should not fall back to latest format version.
            # => 'format_version' may be invalid or the issue lies with 'type_'...
            raise e

    downgrade_format_version = odv and Version(sub_spec.format_version) < odv
    if downgrade_format_version:
        warnings.warn(
            f"Loading future {type_} format version {original_data_version} as (latest known) "
            f"{sub_spec.format_version}."
        )
        data["format_version"] = sub_spec.format_version  # set format_version to latest available

        # save original format version under config:bioimageio:original_format_version for reference
        if "config" not in data:
            data["config"] = {}

        if "bioimageio" not in data["config"]:
            data["config"]["bioimageio"] = {}

        data["config"]["bioimageio"]["original_format_version"] = original_data_version

    schema: SharedBioImageIOSchema = getattr(sub_spec.schema, class_name)()

    data = sub_spec.converters.maybe_convert(data)
    try:
        raw_rd = schema.load(data)
    except ValidationError as e:
        if downgrade_format_version:
            e.messages["format_version"] = (
                f"Other errors may be caused by a possibly incompatible future format version {original_data_version} "
                f"treated as {sub_spec.format_version}."
            )

        raise e

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


def get_description_class(type_: str, format_version: str = "latest"):
    if type_ == "generic":
        return ""
    else:
        return type_.title()
