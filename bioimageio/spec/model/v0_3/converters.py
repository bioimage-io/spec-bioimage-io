import copy
import pathlib
from typing import Any, Dict

from marshmallow import Schema

from . import raw_nodes, schema

AUTO_CONVERTED_DOCUMENTATION_FILE_NAME = "auto_converted_documentation.md"


def convert_model_v0_3_1_to_v0_3_2(data: Dict[str, Any]) -> Dict[str, Any]:
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

            weights_entry["authors"] = [{"name": name} for name in weights_entry["authors"]]
            authors_update = future.get("weights", {}).get(weights_format, {}).get("authors")
            if authors_update is not None:
                for a, u in zip(weights_entry["authors"], authors_update):
                    a.update(u)

    # documentation: we now enforce `documentation` to be a local md file
    if "documentation" in data:

        class DocSchema(Schema):
            doc = schema.Model().fields["documentation"]

        doc_errors = DocSchema().validate({"doc": data["documentation"]})
        if doc_errors:
            # data["documentation"] is not a local relative md file, so we replace it with a placeholder.
            # Having access only to the raw data dict, we cannot write the AUTO_CONVERTED_DOCUMENTATION_FILE_NAME file, but
            # save the original content of data["documentation"] in data["config"][AUTO_CONVERTED_DOCUMENTATION_FILE_NAME]
            # to be written to AUTO_CONVERTED_DOCUMENTATION_FILE_NAME at a later stage.
            data["config"] = data.get("config", {})  # make sure config exists
            if AUTO_CONVERTED_DOCUMENTATION_FILE_NAME not in data["config"]:
                orig_doc = data["documentation"]
                assert isinstance(orig_doc, str)
                if orig_doc.startswith("http"):
                    if orig_doc.endswith(".md"):
                        doc = raw_nodes.URI(orig_doc)
                    else:
                        doc = f"Find documentation at {orig_doc}"
                else:
                    doc = pathlib.Path(orig_doc)

                data["config"][AUTO_CONVERTED_DOCUMENTATION_FILE_NAME] = doc
                data["documentation"] = AUTO_CONVERTED_DOCUMENTATION_FILE_NAME

    # model version
    if "version" in future:
        data["version"] = future.pop("version")

    return data


def convert_model_v0_3_2_to_v0_3_3(data: Dict[str, Any]) -> Dict[str, Any]:
    data["format_version"] = "0.3.3"
    if "outputs" in data:
        for out in data["outputs"]:
            if "shape" in out:
                shape = out["shape"]
                if isinstance(shape, dict) and "reference_input" in shape:
                    shape["reference_tensor"] = shape.pop("reference_input")

    return data


def maybe_convert(data: Dict[str, Any]) -> Dict[str, Any]:
    """auto converts model 'data' to newest format"""

    data = copy.deepcopy(data)

    if data.get("format_version", "0.3.0") == "0.3.0":
        # no breaking change, bump to 0.3.1
        data["format_version"] = "0.3.1"

    if data["format_version"] == "0.3.1":
        data = convert_model_v0_3_1_to_v0_3_2(data)

    if data["format_version"] == "0.3.2":
        data = convert_model_v0_3_2_to_v0_3_3(data)

    if data["format_version"] in ("0.3.3", "0.3.4", "0.3.5"):
        data["format_version"] = "0.3.6"

    # remove 'future' from config if no other than the used future entries exist
    config = data.get("config", {})
    if config.get("future") == {}:
        del config["future"]

    # remove 'config' if now empty
    if data.get("config") == {}:
        del data["config"]

    return data
