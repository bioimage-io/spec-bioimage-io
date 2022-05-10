import warnings
from pathlib import Path
from typing import Any, Dict, Union

from bioimageio.spec.shared import resolve_rdf_source
from .imjoy_plugin_parser import get_plugin_as_rdf  # type: ignore
from ..shared.raw_nodes import URI


def enrich_partial_rdf_with_imjoy_plugin(partial_rdf: Dict[str, Any], root: Union[URI, Path]) -> Dict[str, Any]:
    """
    a (partial) rdf may have 'rdf_resource' or 'source' which resolve to rdf data that may be overwritten.
    Due to resolving imjoy plugins this is not done in bioimageio.spec.collection atm
    """

    enriched_rdf = {}
    if "rdf_source" in partial_rdf:
        rdf_source = partial_rdf["rdf_source"]
        if isinstance(rdf_source, str) and rdf_source.split("?")[0].endswith(".imjoy.html"):
            # rdf_source is an imjoy plugin
            rdf_source = dict(get_plugin_as_rdf(rdf_source))

        else:
            # rdf_source is an actual rdf
            if not isinstance(rdf_source, dict):
                try:
                    rdf_source, rdf_source_name, rdf_source_root = resolve_rdf_source(rdf_source)
                except Exception as e:
                    try:
                        rdf_source, rdf_source_name, rdf_source_root = resolve_rdf_source(root / rdf_source)
                    except Exception as ee:
                        rdf_source = {}
                        warnings.warn(f"Failed to resolve `rdf_source`: 1. {e}\n2. {ee}")
                    else:
                        rdf_source["root_path"] = rdf_source_root  # enables remote source content to be resolved
                else:
                    rdf_source["root_path"] = rdf_source_root  # enables remote source content to be resolved

        assert isinstance(rdf_source, dict)
        enriched_rdf.update(rdf_source)

    if "source" in partial_rdf:
        if partial_rdf["source"].split("?")[0].endswith(".imjoy.html"):
            rdf_from_source = get_plugin_as_rdf(partial_rdf["source"])
            enriched_rdf.update(rdf_from_source)

    enriched_rdf.update(partial_rdf)  # initial partial rdf overwrites fields from rdf_source or source
    return enriched_rdf
