import os
import traceback
import warnings
from typing import Dict, IO, Optional, Union

from marshmallow import ValidationError

from .io_ import load_raw_resource_description, resolve_rdf_source
from .shared.common import nested_default_dict_as_nested_dict

KNOWN_COLLECTION_CATEGORIES = ("application", "collection", "dataset", "model", "notebook")


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
        A summary dict with "error", "traceback" and "nested_errors" keys.
    """
    if verbose != "deprecated":
        warnings.warn("'verbose' flag is deprecated")

    if update_format_inner is None:
        update_format_inner = update_format

    error = None
    tb = None
    nested_errors: Dict[str, list] = {}
    try:
        rdf_source, source_name, root = resolve_rdf_source(rdf_source)
    except Exception as e:
        error = str(e)
        tb = traceback.format_tb(e.__traceback__)
        try:
            source_name = str(rdf_source)
        except Exception as e:
            source_name = str(e)

    if not isinstance(rdf_source, dict):
        error = f"expected loaded resource to be a dictionary, but got type {type(rdf_source)}: {str(rdf_source)}"

    raw_rd = None
    if error is None:
        try:
            raw_rd = load_raw_resource_description(rdf_source, update_to_current_format=update_format)
        except ValidationError as e:
            error = nested_default_dict_as_nested_dict(e.normalized_messages())
        except Exception as e:
            error = str(e)
            tb = traceback.format_tb(e.__traceback__)

        if raw_rd is not None and raw_rd.type == "collection":
            for inner_category in KNOWN_COLLECTION_CATEGORIES:
                for inner in getattr(raw_rd, inner_category) or []:
                    try:
                        inner_source = inner.source
                    except Exception as e:
                        inner_summary = {"error": str(e)}
                    else:
                        inner_summary = validate(inner_source, update_format_inner, update_format_inner)

                    if inner_summary["error"] is not None:
                        nested_errors[inner_category] = nested_errors.get(inner_category, []) + [inner_summary]

            if nested_errors:
                error = f"Errors in collections of {list(nested_errors)}"

    return {
        "name": source_name if raw_rd is None else raw_rd.name,
        "source_name": source_name,
        "error": error,
        "traceback": tb,
        "nested_errors": nested_errors,
    }
