import os
import traceback
import warnings
from pathlib import Path
from typing import Any, Callable, Dict, IO, List, Optional, Union
from bioimageio.spec.shared.types import RawMapping

from marshmallow import ValidationError

from .collection.v0_2 import default_enrich_partial_rdf, resolve_collection_entries
from .io_ import (
    load_raw_resource_description,
    resolve_rdf_source,
    save_raw_resource_description,
    serialize_raw_resource_description_to_dict,
)
from .shared import update_nested
from .shared.common import ValidationSummary, ValidationWarning, nested_default_dict_as_nested_dict, yaml
from .shared.raw_nodes import ResourceDescription as RawResourceDescription, URI
from .v import __version__


def update_format(
    rdf_source: Union[dict, os.PathLike, IO, str, bytes],
    path: Union[os.PathLike, str],
    update_to_format: str = "latest",
):
    """Auto-update fields of a bioimage.io resource"""
    raw = load_raw_resource_description(rdf_source, update_to_format=update_to_format)
    save_raw_resource_description(raw, Path(path))


    # update_format_inner: Optional[bool] = None,
    # load_rdf_source: Callable[[dict, Union[URI, Path]], dict] = default_enrich_partial_rdf,

        # update_format_inner: (applicable to `collections` resources only) `update_format` for nested resources
        # enrich_partial_rdf: (optional) callable to customize RDF data on the fly.
        #                     Don't use this if you don't know exactly what to do with it.

    # if update_format_inner is None:
    #     update_format_inner = update_format

def validate(
    resource_description: RawMapping,
    update_format: bool = False,
) -> ValidationSummary:
    """Validate a bioimage.io resource description, i.e. the content of a resource description file (RDF).

    Args:
        resource_description: raw resource description (e.g. loaded from an rdf.yaml file).
        update_format: weather or not to apply auto-conversion to the latest format version before validation

    Returns:
        A summary dict with keys:
            bioimageio_spec_version,
            error,
            name,
            nested_errors,
            source_name,
            status,
            traceback,
            warnings,
    """

    error: Union[None, str, Dict[str, Any]] = None
    tb = None
    nested_errors: Dict[str, Dict[str, Any]] = {}



        if isinstance(rdf_source, RawResourceDescription):
            source_name = rdf_source.name
        else:
            try:
                rdf_source_preview, source_name, root = resolve_rdf_source(rdf_source)
            except Exception as e:
                error = str(e)
                tb = traceback.format_tb(e.__traceback__)
                try:
                    source_name = str(rdf_source)
                except Exception as e:
                    source_name = str(e)
            else:
                if not isinstance(rdf_source_preview, dict):
                    error = f"expected loaded resource to be a dictionary, but got type {type(rdf_source_preview)}"

        all_warnings = warnings1 or []
    raw_rd = None
    format_version = ""
    resource_type = ""
    if not error:
        with warnings.catch_warnings(record=True) as warnings2:
            try:
                raw_rd = load_raw_resource_description(rdf_source, update_to_format="latest" if update_format else None)
            except ValidationError as e:
                error = nested_default_dict_as_nested_dict(e.normalized_messages())
            except Exception as e:
                error = str(e)
                tb = traceback.format_tb(e.__traceback__)

            if raw_rd is not None:
                format_version = raw_rd.format_version
                resource_type = "general" if raw_rd.type == "rdf" else raw_rd.type

            if raw_rd is not None and raw_rd.type == "collection":
                assert hasattr(raw_rd, "collection")
                for idx, (entry_rdf, entry_error) in enumerate(resolve_collection_entries(raw_rd, enrich_partial_rdf=enrich_partial_rdf)):  # type: ignore
                    if entry_error:
                        entry_summary: Union[Dict[str, str], ValidationSummary] = {"error": entry_error}
                    else:
                        assert isinstance(entry_rdf, RawResourceDescription)
                        entry_summary = validate(
                            entry_rdf, update_format=update_format, update_format_inner=update_format_inner
                        )

                        wrns: Union[str, dict] = entry_summary.get("warnings", {})
                        assert isinstance(wrns, dict)
                        id_info = f"(id={entry_rdf.id}) " if hasattr(entry_rdf, "id") else ""  # type: ignore
                        for k, v in wrns.items():
                            warnings.warn(f"collection[{idx}]:{k}: {id_info}{v}", category=ValidationWarning)

                    if entry_summary["error"]:
                        if "collection" not in nested_errors:
                            nested_errors["collection"] = {}

                        nested_errors["collection"][idx] = entry_summary["error"]

                if nested_errors:
                    # todo: make short error message and refer to 'nested_errors' or deprecated 'nested_errors'
                    error = nested_errors

            all_warnings += warnings2 or []

    return {
        "bioimageio_spec_version": __version__,
        "error": error,
        "name": (
            f"bioimageio.spec static validation of {resource_type} RDF {format_version}"
            f"{' with update to latest format version' if update_format else ''}"
        ),
        "nested_errors": nested_errors,
        "source_name": source_name,
        "status": "passed" if error is None else "failed",
        "traceback": tb,
        "warnings": ValidationWarning.get_warning_summary(all_warnings),
    }


def update_rdf(
    source: Union[RawResourceDescription, dict, os.PathLike, IO, str, bytes],
    update: Union[RawResourceDescription, dict, os.PathLike, IO, str, bytes],
    output: Union[None, dict, os.PathLike] = None,
    validate_output: bool = True,
) -> Union[dict, Path, RawResourceDescription]:
    """
    Args:
        source:  source of RDF
        update:  a (partial) RDF used as update
        output:  dict or path to write output to (default: return new dict)
        validate_output: whether or not to validate the updated RDF

    Returns:
        The updated content of the source rdf as dict or,
        if output is a path, that path (where the updated content is saved to).

    Raises:
        ValidationError: if `validate_output` and the updated rdf does not pass validation
    """
    if isinstance(source, RawResourceDescription):
        src = source
    else:
        src = load_raw_resource_description(source)

    up = resolve_rdf_source(update)

    if src.root_path != up.root and not validate_output:
        warnings.warn(
            f"root path of source {src.name} and update {up.name} differ. Relative paths might be invalid in the output."
        )

    out_data = update_nested(src, up.data)
    assert isinstance(out_data, (RawResourceDescription, dict))
    if validate_output:
        summary = validate(out_data)
        if summary["warnings"]:
            warnings.warn(f"updated rdf validation warnings\n: {summary['warnings']}")
        if summary["status"] != "passed":
            msg = f"updated rdf did not pass validation; status: {summary['status']}"
            if summary["error"]:
                msg += f"; error: {summary['error']}"

            raise ValidationError(msg)

    if output is None:
        if isinstance(source, RawResourceDescription):
            return load_raw_resource_description(out_data)
        else:
            output = {}

    if isinstance(output, dict):
        if isinstance(out_data, RawResourceDescription):
            out_data = serialize_raw_resource_description_to_dict(out_data, convert_absolute_paths=False)

        assert isinstance(out_data, dict)
        output.update(out_data)
        return output
    else:
        assert yaml is not None
        output = Path(output)
        if isinstance(out_data, RawResourceDescription):
            out_data.root_path = output.parent
            try:
                out_data = serialize_raw_resource_description_to_dict(out_data, convert_absolute_paths=True)
            except ValueError as e:
                warnings.warn(
                    f"Failed to convert paths in updated rdf to relative paths with root {output}; error: {e}"
                )
                warnings.warn(f"updated rdf at {output} contains absolute paths and is thus invalid!")
                assert isinstance(out_data, RawResourceDescription)
                out_data = serialize_raw_resource_description_to_dict(out_data, convert_absolute_paths=False)

        yaml.dump(out_data, output)
        return output

def get_resource_package_content_wo_rdf(
    raw_rd: Union[GenericRawRD, raw_nodes.URI, str, pathlib.Path],
    *,
    weights_priority_order: Optional[Sequence[str]] = None,  # model only
) -> Tuple[raw_nodes.ResourceDescription, Dict[str, Union[pathlib.PurePath, raw_nodes.URI]]]:
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
    if isinstance(raw_rd, raw_nodes.ResourceDescription):
        r_rd = raw_rd
    else:
        r_rd = load_raw_resource_description(raw_rd)

    sub_spec = _get_spec_submodule(r_rd.type, r_rd.format_version)
    if r_rd.type == "model":
        filter_kwargs = dict(weights_priority_order=weights_priority_order)
    else:
        filter_kwargs = {}

    r_rd = sub_spec.utils.filter_resource_description(r_rd, **filter_kwargs)

    content: Dict[str, Union[pathlib.PurePath, raw_nodes.URI]] = {}
    r_rd = RawNodePackageTransformer(content, r_rd.root_path).transform(r_rd)
    assert "rdf.yaml" not in content
    return r_rd, content


def get_resource_package_content(
    raw_rd: Union[raw_nodes.ResourceDescription, raw_nodes.URI, str, pathlib.Path],
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

    r_rd, content = get_resource_package_content_wo_rdf(raw_rd, weights_priority_order=weights_priority_order)
    return {**content, **{"rdf.yaml": serialize_raw_resource_description(r_rd)}}




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
