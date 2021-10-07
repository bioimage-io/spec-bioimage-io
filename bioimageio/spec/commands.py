import os
import traceback
from typing import Dict, IO, List, Sequence, Union

from marshmallow import ValidationError

from .io_ import load_raw_resource_description
from .shared.utils import resolve_rdf_source


def validate(
    rdf_source: Union[dict, os.PathLike, IO, str, bytes],
    update_format: bool = False,
    update_format_inner: bool = None,
    verbose: bool = False,
) -> Dict[str, Union[str, list, dict]]:
    """Validate a BioImage.IO Resource Description File (RDF)."""
    if update_format_inner is None:
        update_format_inner = update_format

    source_name, rdf_source = resolve_rdf_source(rdf_source)
    try:
        raw_rd = load_raw_resource_description(rdf_source, update_to_current_format=update_format)
    except ValidationError as e:
        return {source_name: e.normalized_messages()}
    except Exception as e:
        if verbose:
            msg: Union[str, Dict[str, Union[str, Sequence[str]]]] = {
                "error": str(e),
                "traceback": traceback.format_tb(e.__traceback__),
            }
        else:
            msg = str(e)

        return {source_name: msg}

    collection_errors: List[Union[str, dict]] = []
    if raw_rd.type == "collection":
        for inner_category in ["application", "collection", "dataset", "model", "notebook"]:
            for inner in getattr(raw_rd, inner_category) or []:
                try:
                    inner_source = inner.source
                except Exception as e:
                    collection_errors.append(str(e))
                else:
                    inner_errors = validate(inner_source, update_format_inner, update_format_inner, verbose)
                    if inner_errors:
                        collection_errors.append(inner_errors)

    if collection_errors:
        return {source_name: collection_errors}
    else:
        return {}
