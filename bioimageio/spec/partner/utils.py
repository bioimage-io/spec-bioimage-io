from urllib.parse import urljoin
import warnings
from pathlib import Path
from typing import Any, Callable, Dict, Tuple, Union

from pydantic import DirectoryPath, FilePath, HttpUrl

from .imjoy_plugin_parser import get_plugin_as_rdf


def enrich_partial_rdf_with_imjoy_plugin(
    partial_rdf: Dict[str, Any],
    root: Union[HttpUrl, DirectoryPath],
    resolve_rdf_source: Callable[
        [Union[HttpUrl, FilePath, str]], Tuple[Dict[str, Any], str, Union[HttpUrl, DirectoryPath]]
    ],
) -> Dict[str, Any]:
    """
    a (partial) rdf may have 'rdf_source' or 'source' which resolve to rdf data that may be overwritten.
    Due to resolving imjoy plugins this is not done in bioimageio.spec.collection atm
    """

    enriched_rdf: Dict[str, Any] = {}
    if "rdf_source" in partial_rdf:
        given_rdf_src = partial_rdf["rdf_source"]
        if isinstance(given_rdf_src, str) and given_rdf_src.split("?")[0].endswith(".imjoy.html"):
            # given_rdf_src is an imjoy plugin
            rdf_source = dict(get_plugin_as_rdf(given_rdf_src))
        else:
            # given_rdf_src is an actual rdf
            if isinstance(given_rdf_src, dict):
                rdf_source: Dict[str, Any] = given_rdf_src
            else:
                try:
                    rdf_source, _, rdf_source_root = resolve_rdf_source(given_rdf_src)
                except Exception as e:
                    try:
                        rdf_source, _, rdf_source_root = resolve_rdf_source(
                            root / given_rdf_src if isinstance(root, Path) else urljoin(str(root), given_rdf_src)
                        )
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
