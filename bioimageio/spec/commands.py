import os
import traceback
import warnings
from pathlib import Path
from typing import Any, Callable, Dict, IO, List, Optional, Union

from marshmallow import ValidationError

from .collection.v0_2.utils import default_enrich_partial_rdf, resolve_collection_entries
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
    """Update a BioImage.IO resource"""
    raw = load_raw_resource_description(rdf_source, update_to_format=update_to_format)
    save_raw_resource_description(raw, Path(path))


def validate(
    rdf_source: Union[RawResourceDescription, dict, os.PathLike, IO, str, bytes],
    update_format: bool = False,
    update_format_inner: bool = None,
    verbose: bool = "deprecated",  # type: ignore
    enrich_partial_rdf: Callable[[dict, Union[URI, Path]], dict] = default_enrich_partial_rdf,
) -> ValidationSummary:
    """Validate a BioImage.IO Resource Description File (RDF).

    Args:
        rdf_source: resource description as path, url or bytes of an RDF or packaged resource, or as yaml string or dict
        update_format: weather or not to apply auto-conversion to the latest format version before validation
        update_format_inner: (applicable to `collections` resources only) `update_format` for nested resources
        verbose: deprecated
        enrich_partial_rdf: (optional) callable to customize RDF data on the fly.
                            Don't use this if you don't know exactly what to do with it.

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
    if verbose != "deprecated":
        warnings.warn("'verbose' flag is deprecated")

    if update_format_inner is None:
        update_format_inner = update_format

    error: Union[None, str, Dict[str, Any]] = None
    tb = None
    nested_errors: Dict[str, dict] = {}
    with warnings.catch_warnings(record=True) as warnings1:
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
    output: Union[dict, os.PathLike] = None,
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
                out_data = serialize_raw_resource_description_to_dict(out_data, convert_absolute_paths=False)

        yaml.dump(out_data, output)
        return output
