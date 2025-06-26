# pragma: no cover
# type: ignore
"""ImJoy plugin parser module."""
import copy
import json
import uuid
import warnings
from pathlib import Path
from typing import Any, Callable, Dict, Tuple, Union
from urllib.parse import urljoin

import httpx
from pydantic import DirectoryPath, FilePath, HttpUrl
from ruyaml import YAML

yaml = YAML(typ="safe")

tag_types = ["config", "script", "link", "window", "style", "docs", "attachment"]

CONFIGURABLE_FIELDS = [
    "env",
    "requirements",
    "dependencies",
    "icon",
    "ui",
    "type",
    "flags",
    "labels",
    "cover",
    "base_frame",
    "base_worker",
    "passive",
]


class dotdict(dict):  # pylint: disable=invalid-name
    """Access dictionary attributes with dot.notation."""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __deepcopy__(self, memo=None):
        """Make a deep copy."""
        return dotdict(copy.deepcopy(dict(self), memo=memo))


def parse_imjoy_plugin(source, overwrite_config=None):
    """Parse ImJoy plugin file and return a dict with all the fields."""
    from lxml import etree

    root = etree.HTML("<html>" + source + "</html>")
    plugin_comp = dotdict()
    for tag_type in tag_types:
        elms = root.xpath(f".//{tag_type}")
        values = []
        for elm in elms:
            values.append(
                dotdict(
                    attrs=dotdict(elm.attrib),
                    content=elm.text,
                )
            )
        plugin_comp[tag_type] = values
    if plugin_comp.config[0].attrs.lang == "yaml":
        config = yaml.load(plugin_comp.config[0].content)
    elif plugin_comp.config[0].attrs.lang == "json":
        config = json.loads(plugin_comp.config[0].content)
    else:
        raise Exception(
            "Unsupported config language: " + plugin_comp.config[0].attrs.lang
        )

    overwrite_config = overwrite_config or {}
    config["tag"] = overwrite_config.get("tag") or (
        config.get("tags") and config.get("tags")[0]
    )
    config["hot_reloading"] = overwrite_config.get("hot_reloading")
    config["scripts"] = []
    # try to match the script with current tag
    for elm in plugin_comp.script:
        if elm.attrs.tag == config["tag"]:
            config["script"] = elm.content
        # exclude script with mismatched tag
        if not elm.attrs.tag or elm.attrs.tag == config["tag"]:
            config["scripts"].append(elm)
    if not config.get("script") and len(plugin_comp.script) > 0:
        config["script"] = plugin_comp.script[0].content
        config["lang"] = plugin_comp.script[0].attrs.lang
    config["links"] = plugin_comp.link or None
    config["windows"] = plugin_comp.window or None
    config["styles"] = plugin_comp.style or None
    config["docs"] = plugin_comp.docs[0] if plugin_comp.docs else config.get("docs")
    config["attachments"] = plugin_comp.attachment or None

    config["_id"] = overwrite_config.get("_id") or config.get("name").replace(" ", "_")
    config["uri"] = overwrite_config.get("uri")
    config["origin"] = overwrite_config.get("origin")
    config["namespace"] = overwrite_config.get("namespace")
    config["code"] = source
    config["id"] = (
        config.get("name").strip().replace(" ", "_") + "_" + str(uuid.uuid4())
    )
    config["runnable"] = config.get("runnable", True)
    config["requirements"] = config.get("requirements") or []

    for field in CONFIGURABLE_FIELDS:
        obj = config.get(field)
        if obj and isinstance(obj, dict) and not isinstance(obj, list):
            if config.get("tag"):
                config[field] = obj.get(config.get("tag"))
                if not obj.get(config.get("tag")):
                    print(
                        "WARNING: "
                        + field
                        + " do not contain a tag named: "
                        + config.get("tag")
                    )
            else:
                raise Exception("You must use 'tags' with configurable fields.")
    config["lang"] = config.get("lang") or "javascript"
    return config


def convert_config_to_rdf(plugin_config, source_url=None) -> dict:
    """Convert imjoy plugin config to RDF format."""
    rdf = {
        "type": "application",
    }
    if source_url:
        rdf["source"] = source_url
    fields = [
        "icon",
        "name",
        "version",
        "api_version",
        "description",
        "license",
        "requirements",
        "dependencies",
        "env",
        "passive",
        "services",
    ]
    for field in fields:
        if field in plugin_config:
            rdf[field] = plugin_config[field]
    tags = plugin_config.get("labels", []) + plugin_config.get("flags", [])
    if "bioengine" not in tags:
        tags.append("bioengine")
    rdf["tags"] = tags

    # docs = plugin_config.get("docs")
    #     if isinstance(docs, dict):
    #         rdf["documentation"] = docs.get("content")
    #     elif isinstance(docs, str):
    #         rdf["documentation"] = docs
    rdf["covers"] = plugin_config.get("cover")
    # make sure we have a list
    if not rdf["covers"]:
        rdf["covers"] = []
    elif not isinstance(rdf["covers"], list):
        rdf["covers"] = [rdf["covers"]]

    rdf["badges"] = plugin_config.get("badge")
    if not rdf["badges"]:
        rdf["badges"] = []
    elif not isinstance(rdf["badges"], list):
        rdf["badges"] = [rdf["badges"]]

    authors = plugin_config.get("author")
    if authors:
        if isinstance(authors, str):
            authors = {"name": authors}
        if not isinstance(authors, list):
            authors = [authors]
        rdf["authors"] = authors

    return rdf


def get_plugin_as_rdf(source_url: str) -> Dict[Any, Any]:
    """Get imjoy plugin config in RDF format."""
    req = httpx.get(source_url, timeout=5)
    source = req.text
    plugin_config = parse_imjoy_plugin(source)
    rdf = convert_config_to_rdf(plugin_config, source_url)
    return rdf


def enrich_partial_rdf_with_imjoy_plugin(
    partial_rdf: Dict[str, Any],
    root: Union[HttpUrl, DirectoryPath],
    resolve_rdf_source: Callable[
        [Union[HttpUrl, FilePath, str]],
        Tuple[Dict[str, Any], str, Union[HttpUrl, DirectoryPath]],
    ],
) -> Dict[str, Any]:
    """
    a (partial) rdf may have 'rdf_source' or 'source' which resolve to rdf data that may be overwritten.
    """

    enriched_rdf: Dict[str, Any] = {}
    if "rdf_source" in partial_rdf:
        given_rdf_src = partial_rdf["rdf_source"]
        if isinstance(given_rdf_src, str) and given_rdf_src.split("?")[0].endswith(
            ".imjoy.html"
        ):
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
                            root / given_rdf_src
                            if isinstance(root, Path)
                            else urljoin(str(root), given_rdf_src)
                        )
                    except Exception as ee:
                        rdf_source = {}
                        warnings.warn(
                            f"Failed to resolve `rdf_source`: 1. {e}\n2. {ee}"
                        )
                    else:
                        rdf_source["root_path"] = (
                            rdf_source_root  # enables remote source content to be resolved
                        )
                else:
                    rdf_source["root_path"] = (
                        rdf_source_root  # enables remote source content to be resolved
                    )

        assert isinstance(rdf_source, dict)
        enriched_rdf.update(rdf_source)

    if "source" in partial_rdf:
        if partial_rdf["source"].split("?")[0].endswith(".imjoy.html"):
            rdf_from_source = get_plugin_as_rdf(partial_rdf["source"])
            enriched_rdf.update(rdf_from_source)

    enriched_rdf.update(
        partial_rdf
    )  # initial partial rdf overwrites fields from rdf_source or source
    return enriched_rdf
