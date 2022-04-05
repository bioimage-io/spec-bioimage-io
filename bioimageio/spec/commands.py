import os
import traceback
import warnings
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, IO, List, Optional, Union

from marshmallow import ValidationError

from .collection.v0_2.utils import resolve_collection_entries
from .io_ import (
    load_raw_resource_description,
    resolve_rdf_source,
    save_raw_resource_description,
    serialize_raw_resource_description_to_dict,
)
from .shared import update_nested
from .shared.common import ValidationWarning, nested_default_dict_as_nested_dict, yaml
from .shared.raw_nodes import ResourceDescription as RawResourceDescription
from .v import __version__

try:
    from typing import TypedDict, Literal
except ImportError:
    from typing_extensions import TypedDict, Literal  # type: ignore


def update_format(
    rdf_source: Union[dict, os.PathLike, IO, str, bytes],
    path: Union[os.PathLike, str],
    update_to_format: str = "latest",
):
    """Update a BioImage.IO resource"""
    raw = load_raw_resource_description(rdf_source, update_to_format=update_to_format)
    save_raw_resource_description(raw, Path(path))


class ValidationSummary(TypedDict):
    bioimageio_spec_version: str
    error: Union[None, str, Dict[str, Any]]
    name: str
    nested_errors: Dict[str, dict]
    source_name: str
    status: Union[Literal["passed", "failed"], str]
    traceback: Optional[List[str]]
    warnings: dict


def validate(
    rdf_source: Union[RawResourceDescription, dict, os.PathLike, IO, str, bytes],
    update_format: bool = False,
    update_format_inner: bool = None,
    verbose: bool = "deprecated",  # type: ignore
) -> ValidationSummary:
    """Validate a BioImage.IO Resource Description File (RDF).

    Args:
        rdf_source: resource description as path, url or bytes of an RDF or packaged resource, or as yaml string or dict
        update_format: weather or not to apply auto-conversion to the latest format version before validation
        update_format_inner: (applicable to `collections` resources only) `update_format` for nested resources
        verbose: deprecated

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
    if isinstance(rdf_source, RawResourceDescription):
        source_name = rdf_source.name
        root = rdf_source.root_path
    else:
        try:
            rdf_source, source_name, root = resolve_rdf_source(rdf_source)
        except Exception as e:
            error = str(e)
            tb = traceback.format_tb(e.__traceback__)
            try:
                source_name = str(rdf_source)
            except Exception as e:
                source_name = str(e)
        else:
            if not isinstance(rdf_source, dict):
                error = (
                    f"expected loaded resource to be a dictionary, but got type {type(rdf_source)}: {str(rdf_source)}"
                )

    raw_rd = None
    format_version = ""
    resource_type = ""
    if error:
        validation_warnings = []
    else:
        with warnings.catch_warnings(record=True) as all_warnings:
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
                for idx, (rdf_data, entry_error) in enumerate(resolve_collection_entries(raw_rd)):  # type: ignore
                    if entry_error:
                        entry_summary = {"error": entry_error}
                    else:
                        # apparently a mypy bug: TypedDict is not a dict.
                        entry_summary = validate(  # type: ignore
                            rdf_data, update_format=update_format, update_format_inner=update_format_inner
                        )

                        wrns: Union[str, dict] = entry_summary.get("warnings", {})
                        assert isinstance(wrns, dict)
                        id_info = f"(id={rdf_data['id']}) " if "id" in rdf_data else ""
                        for k, v in wrns.items():
                            warnings.warn(f"collection[{idx}]:{k}: {id_info}{v}", category=ValidationWarning)

                    if entry_summary["error"]:
                        if "collection" not in nested_errors:
                            nested_errors["collection"] = {}

                        nested_errors["collection"][idx] = entry_summary["error"]

                if nested_errors:
                    # todo: make short error message and refer to 'nested_errors' or deprecated 'nested_errors'
                    error = nested_errors

        validation_warnings = [w for w in all_warnings if issubclass(w.category, ValidationWarning)]

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
        "warnings": ValidationWarning.get_warning_summary(validation_warnings),
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
        src_data = source
        src_name = source.name
        root = source.root_path
    else:
        src_data, src_name, root = resolve_rdf_source(source)

    up = resolve_rdf_source(update)

    if root != up.root and not validate:
        warnings.warn(
            f"root path of source {src_name} and update {up.name} differ. Relative paths might be invalid in the output."
        )

    out_data = update_nested(src_data, up.data)
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
        assert isinstance(out_data, dict)
        output.update(out_data)
        return output
    else:
        assert yaml is not None
        output = Path(output)
        yaml.dump(out_data, output)
        return output
