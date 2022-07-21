import copy
from typing import Any, Dict

from marshmallow import missing

from bioimageio.spec.rdf.v0_2.converters import remove_slash_from_names


def convert_model_from_v0_3_to_0_4_0(data: Dict[str, Any]) -> Dict[str, Any]:
    from bioimageio.spec.model import v0_3

    data = copy.deepcopy(data)

    data = v0_3.converters.maybe_convert(data)
    v0_3.schema.Model().validate(data)

    data.pop("language", None)
    data.pop("framework", None)

    architecture = data.pop("source", missing)
    architecture_sha256 = data.pop("sha256", missing)
    kwargs = data.pop("kwargs", missing)
    pytorch_state_dict_weights_entry = data.get("weights", {}).get("pytorch_state_dict")
    if pytorch_state_dict_weights_entry is not None:
        if architecture is not missing:
            pytorch_state_dict_weights_entry["architecture"] = architecture

        if architecture_sha256 is not missing:
            pytorch_state_dict_weights_entry["architecture_sha256"] = architecture_sha256

        if kwargs is not missing:
            pytorch_state_dict_weights_entry["kwargs"] = kwargs

    torchscript_weights_entry = data.get("weights", {}).pop("pytorch_script", None)
    if torchscript_weights_entry is not None:
        data["weights"]["torchscript"] = torchscript_weights_entry

    data["format_version"] = "0.4.0"

    return data


def convert_model_from_v0_4_0_to_0_4_1(data: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(data)

    # move dependencies from root to pytorch_state_dict weights entry
    deps = data.pop("dependencies", None)
    weights = data.get("weights", {})
    if deps and weights and isinstance(weights, dict):
        entry = weights.get("pytorch_state_dict")
        if entry and isinstance(entry, dict):
            entry["dependencies"] = deps

    data["format_version"] = "0.4.1"
    return data


def convert_model_from_v0_4_4_to_0_4_5(data: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(data)

    parent = data.pop("parent", None)
    if parent and "uri" in parent:
        data["parent"] = parent["uri"]

    data["format_version"] = "0.4.5"
    return data


def convert_model_from_v0_4_6_to_0_4_7(data: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(data)

    remove_slash_from_names(data)

    data["format_version"] = "0.4.7"
    return data


def maybe_convert(data: Dict[str, Any]) -> Dict[str, Any]:
    """auto converts model 'data' to newest format"""
    major, minor, patch = map(int, data.get("format_version", "0.3.0").split("."))
    if major == 0 and minor < 4:
        data = convert_model_from_v0_3_to_0_4_0(data)

    if data["format_version"] == "0.4.0":
        data = convert_model_from_v0_4_0_to_0_4_1(data)

    if data["format_version"] in ("0.4.1", "0.4.2", "0.4.3"):
        data["format_version"] = "0.4.4"

    if data["format_version"] == "0.4.4":
        data = convert_model_from_v0_4_4_to_0_4_5(data)

    if data["format_version"] == "0.4.5":
        data["format_version"] = "0.4.6"

    if data["format_version"] == "0.4.6":
        data = convert_model_from_v0_4_6_to_0_4_7(data)

    # remove 'future' from config if no other than the used future entries exist
    config = data.get("config", {})
    if config.get("future") == {}:
        del config["future"]

    # remove 'config' if now empty
    if data.get("config") == {}:
        del data["config"]

    return data
