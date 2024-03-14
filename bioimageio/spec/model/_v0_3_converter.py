# type: ignore
from typing import Any, Dict


def convert_model_from_v0_3_to_0_4_0(data: Dict[str, Any]) -> None:
    """auto converts model 'data' to newest format"""

    if "format_version" not in data:
        return

    if data["format_version"] == "0.3.0":
        # no breaking change, bump to 0.3.1
        data["format_version"] = "0.3.1"

    if data["format_version"] == "0.3.1":
        data = _convert_model_v0_3_1_to_v0_3_2(data)

    if data["format_version"] == "0.3.2":
        data = _convert_model_v0_3_2_to_v0_3_3(data)

    if data["format_version"] in ("0.3.3", "0.3.4", "0.3.5"):
        data["format_version"] = "0.3.6"

    if data["format_version"] != "0.3.6":
        return

    # remove 'future' from config if no other than the used future entries exist
    config = data.get("config", {})
    if config.get("future") == {}:
        del config["future"]

    # remove 'config' if now empty
    if data.get("config") == {}:
        del data["config"]

    data.pop("language", None)
    data.pop("framework", None)

    architecture = data.pop("source", None)
    architecture_sha256 = data.pop("sha256", None)
    kwargs = data.pop("kwargs", None)
    pytorch_state_dict_weights_entry = data.get("weights", {}).get("pytorch_state_dict")
    if pytorch_state_dict_weights_entry is not None:
        if architecture is not None:
            pytorch_state_dict_weights_entry["architecture"] = architecture

        if architecture_sha256 is not None:
            pytorch_state_dict_weights_entry["architecture_sha256"] = (
                architecture_sha256
            )

        if kwargs is not None:
            pytorch_state_dict_weights_entry["kwargs"] = kwargs

    torchscript_weights_entry = data.get("weights", {}).pop("pytorch_script", None)
    if torchscript_weights_entry is not None:
        data.setdefault("weights", {})["torchscript"] = torchscript_weights_entry

    data["format_version"] = "0.4.0"


def _convert_model_v0_3_1_to_v0_3_2(data: Dict[str, Any]) -> Dict[str, Any]:
    data["type"] = "model"
    data["format_version"] = "0.3.2"
    future = data.get("config", {}).get("future", {}).pop("0.3.2", {})

    authors = data.get("authors")
    if isinstance(authors, list):
        data["authors"] = [{"name": name} for name in authors]
        authors_update = future.get("authors")
        if authors_update is not None:
            for a, u in zip(data["authors"], authors_update):
                a.update(u)

    # packaged_by
    packaged_by = data.get("packaged_by")
    if packaged_by is not None:
        data["packaged_by"] = [{"name": name} for name in data["packaged_by"]]
        packaged_by_update = future.get("packaged_by")
        if packaged_by_update is not None:
            for a, u in zip(data["packaged_by"], packaged_by_update):
                a.update(u)

    # authors of weights
    weights = data.get("weights")
    if isinstance(weights, dict):
        for weights_format, weights_entry in weights.items():
            if "authors" not in weights_entry:
                continue

            weights_entry["authors"] = [
                {"name": name} for name in weights_entry["authors"]
            ]
            authors_update = (
                future.get("weights", {}).get(weights_format, {}).get("authors")
            )
            if authors_update is not None:
                for a, u in zip(weights_entry["authors"], authors_update):
                    a.update(u)

    # model version
    if "version" in future:
        data["version"] = future.pop("version")

    return data


def _convert_model_v0_3_2_to_v0_3_3(data: Dict[str, Any]) -> Dict[str, Any]:
    data["format_version"] = "0.3.3"
    if "outputs" in data:
        for out in data["outputs"]:
            if "shape" in out:
                shape = out["shape"]
                if isinstance(shape, dict) and "reference_input" in shape:
                    shape["reference_tensor"] = shape.pop("reference_input")

    return data
