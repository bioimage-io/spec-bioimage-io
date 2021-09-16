import copy
from typing import Any, Dict


def convert_model_from_v0_3(data: Dict[str, Any]) -> Dict[str, Any]:
    from bioimageio.spec.model import v0_3

    data = copy.deepcopy(data)

    data = v0_3.converters.maybe_convert(data)
    v0_3.schema.Model().validate(data)

    data["format_version"] = "0.4.0"

    return data


def maybe_convert(data: Dict[str, Any]) -> Dict[str, Any]:
    """auto converts model 'data' to newest format"""
    major, minor, patch = map(int, data.get("format_version", "0.1.0").split("."))
    if major == 0 and minor < 4:
        data = convert_model_from_v0_3(data)

    # remove 'future' from config if no other than the used future entries exist
    config = data.get("config", {})
    if config.get("future") == {}:
        del config["future"]

    # remove 'config' if now empty
    if data.get("config") == {}:
        del data["config"]

    return data
