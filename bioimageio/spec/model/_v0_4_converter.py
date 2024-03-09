import collections.abc

from .._internal.io import BioimageioYamlContent
from ..generic._v0_2_converter import (
    remove_doi_prefix,
    remove_gh_prefix,
    remove_slashes_from_names,
)
from ._v0_3_converter import convert_model_from_v0_3_to_0_4_0


def convert_from_older_format(data: BioimageioYamlContent) -> None:
    fv = data.get("format_version")
    if not isinstance(fv, str):
        return

    major_minor = tuple(map(int, fv.split(".")[:2]))
    if major_minor < (0, 4):
        convert_model_from_v0_3_to_0_4_0(data)
    elif major_minor > (0, 4):
        return

    if data["format_version"] == "0.4.0":
        _convert_model_from_v0_4_0_to_0_4_1(data)

    if data["format_version"] in ("0.4.1", "0.4.2", "0.4.3", "0.4.4"):
        _convert_model_from_v0_4_4_to_0_4_5(data)

    if data["format_version"] in ("0.4.5", "0.4.6"):
        remove_slashes_from_names(data)
        data["format_version"] = "0.4.7"

    if data["format_version"] in ("0.4.7", "0.4.8"):
        data["format_version"] = "0.4.9"

    if data["format_version"] == "0.4.9":
        if isinstance(config := data.get("config"), dict) and isinstance(
            bconfig := config.get("bioimageio"), dict
        ):
            if (nickname := bconfig.get("nickname")) is not None:
                data["id"] = nickname

            if (nickname_icon := bconfig.get("nickname_icon")) is not None:
                data["id_emoji"] = nickname_icon

        data["format_version"] = "0.4.10"

    remove_doi_prefix(data)
    remove_gh_prefix(data)
    # remove 'future' from config if no other than the used future entries exist
    config = data.get("config", {})
    if isinstance(config, dict) and config.get("future") == {}:
        del config["future"]

    # remove 'config' if now empty
    if data.get("config") == {}:
        del data["config"]


def _convert_model_from_v0_4_0_to_0_4_1(data: BioimageioYamlContent):
    # move dependencies from root to pytorch_state_dict weights entry
    deps = data.pop("dependencies", None)
    weights = data.get("weights", {})
    if deps and weights and isinstance(weights, dict):
        entry = weights.get("pytorch_state_dict")
        if entry and isinstance(entry, dict):
            entry["dependencies"] = deps

    data["format_version"] = "0.4.1"


def _convert_model_from_v0_4_4_to_0_4_5(data: BioimageioYamlContent) -> None:
    parent = data.pop("parent", None)
    if isinstance(parent, collections.abc.Mapping) and "uri" in parent:
        data["parent"] = parent["uri"]

    data["format_version"] = "0.4.5"
