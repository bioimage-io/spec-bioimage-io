import os
import traceback
import warnings
from pathlib import Path
from typing import Any, Dict, IO, Union

from marshmallow import ValidationError

from .collection.v0_2.utils import resolve_collection_entries
from .io_ import (
    load_raw_resource_description,
    resolve_rdf_source,
    save_raw_resource_description,
)
from .shared.common import ValidationWarning, nested_default_dict_as_nested_dict


def update_format(
    rdf_source: Union[dict, os.PathLike, IO, str, bytes],
    path: Union[os.PathLike, str],
    update_to_format: str = "latest",
):
    """Update a BioImage.IO resource"""
    raw = load_raw_resource_description(rdf_source, update_to_format=update_to_format)
    save_raw_resource_description(raw, Path(path))


def validate(
    rdf_source: Union[dict, os.PathLike, IO, str, bytes],
    update_format: bool = False,
    update_format_inner: bool = None,
    verbose: bool = "deprecated",  # type: ignore
) -> dict:
    """Validate a BioImage.IO Resource Description File (RDF).

    Args:
        rdf_source: resource description as path, url or bytes of an RDF or packaged resource, or as yaml string or dict
        update_format: weather or not to apply auto-conversion to the latest format version before validation
        update_format_inner: (applicable to `collections` resources only) `update_format` for nested resources
        verbose: deprecated

    Returns:
        A summary dict with "error", "warnings", "traceback" and "nested_errors" keys.
    """
    if verbose != "deprecated":
        warnings.warn("'verbose' flag is deprecated")

    if update_format_inner is None:
        update_format_inner = update_format

    error: Union[None, str, Dict[str, Any]] = None
    tb = None
    nested_errors: Dict[str, dict] = {}
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
            error = f"expected loaded resource to be a dictionary, but got type {type(rdf_source)}: {str(rdf_source)}"

    raw_rd = None
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

            if raw_rd is not None and raw_rd.type == "collection":
                assert hasattr(raw_rd, "collection")
                for idx, (rdf_data, entry_error) in enumerate(resolve_collection_entries(raw_rd)):  # type: ignore
                    if entry_error:
                        entry_summary = {"error": entry_error}
                    else:
                        entry_summary = validate(
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
                    error = nested_errors

        validation_warnings = [w for w in all_warnings if issubclass(w.category, ValidationWarning)]

    return {
        "name": source_name if raw_rd is None else raw_rd.name,
        "source_name": source_name,
        "error": error,
        "warnings": ValidationWarning.get_warning_summary(validation_warnings),
        "traceback": tb,
        "nested_errors": nested_errors,
    }
