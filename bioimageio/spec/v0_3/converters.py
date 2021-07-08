import copy
import warnings
from collections import defaultdict
from typing import Any, Dict

from marshmallow import Schema

from bioimageio.spec.exceptions import UnconvertibleError
from . import schema

AUTO_CONVERTED_DOCUMENTATION_FILE_NAME = "auto_converted_documentation.md"


def convert_model_from_v0_1(data: Dict[str, Any]) -> Dict[str, Any]:
    from bioimageio.spec import v0_1

    v0_1.schema.Model().validate(data)

    data = copy.deepcopy(data)
    data["format_version"] = "0.3.1"

    data["kwargs"] = {k: None for k in data.pop("required_kwargs", set())}
    data["kwargs"].update(data.pop("optional_kwargs", {}))

    for ipt in data["inputs"]:
        ipt["description"] = ipt["name"]

    for out in data["outputs"]:
        out["description"] = out["name"]

    def rec_dd():
        return defaultdict(rec_dd)

    conversion_errors = rec_dd()
    missing = "MISSING"

    try:
        future = data["config"]["future"].pop("0.3.0")
    except KeyError:
        future = {}

    try:
        future.update(data["config"]["future"].pop("0.3.1"))
    except KeyError:
        pass

    if not future:
        conversion_errors["config"]["future"]["0.3.1"] = missing

    try:
        data["git_repo"] = future.pop("git_repo")
    except KeyError:
        conversion_errors["config"]["future"]["git_repo"] = missing

    try:
        data["timestamp"] = future.pop("timestamp")
    except KeyError:
        conversion_errors["config"]["future"]["timestamp"] = missing

    try:
        weights_format = future.pop("weights_format")
    except KeyError:
        conversion_errors["config"]["future"]["weights_format"] = missing
        weights_format = missing

    additional_weights = future.pop("additional_weights", {})
    if not isinstance(additional_weights, dict):
        conversion_errors["config"]["future"]["additional_weights"] = "expected dict"

    try:
        source = data["prediction"]["weights"].pop("source")
    except KeyError:
        conversion_errors["prediction"]["weights"]["source"] = missing
        source = missing

    try:
        sha256 = data["prediction"]["weights"].pop("hash").pop("sha256")
    except KeyError:
        conversion_errors["prediction"]["weights"]["hash"]["sha256"] = missing
        sha256 = missing

    try:
        data["dependencies"] = data["prediction"].pop("dependencies")
    except KeyError:
        conversion_errors["prediction"]["dependencies"] = missing

    try:
        test_input = data.pop("test_input")
    except KeyError:
        conversion_errors["test_input"] = missing
        test_input = missing

    try:
        test_output = data.pop("test_output")
    except KeyError:
        conversion_errors["test_output"] = missing
        test_output = missing

    data["test_inputs"] = [test_input]
    data["test_outputs"] = [test_output]
    warnings.warn(
        "test_input and test_output need to be converted manually, "
        "as they are split up into files for each individual tensor"
    )
    weights_entry = {
        # "id": weights_future.pop("id", "default"),
        # "name": weights_future.pop("name", "default weights"),
        # "description": weights_future.pop("description", "description"),
        "source": source,
        "sha256": sha256,
        # "tags": weights_future.pop("tags", []),
    }
    weights_future = future.pop("weights", {})
    weights_authors = weights_future.get("authors")
    if weights_authors is not None:
        weights_entry["authors"] = weights_authors

    data["weights"] = {weights_format: weights_entry}
    data["weights"].update(additional_weights)

    if "attachments" in future:
        data["attachments"] = future.pop("attachments")

    if "version" in future:
        data["version"] = future.pop("version")

    for ipt, ipt_fut in zip(data["inputs"], future.get("inputs", [])):
        preprocessing = ipt_fut.get("preprocessing")
        if preprocessing is not None:
            assert "preprocessing" not in ipt
            ipt["preprocessing"] = preprocessing

    for out, out_fut in zip(data["outputs"], future.get("outputs", [])):
        postprocessing = out_fut.get("postprocessing")
        if postprocessing is not None:
            assert "postprocessing" not in out
            out["postprocessing"] = postprocessing

    sample_inputs = future.get("sample_inputs")
    if sample_inputs is not None:
        data["sample_inputs"] = sample_inputs

    sample_outputs = future.get("sample_outputs")
    if sample_outputs is not None:
        data["sample_outputs"] = sample_outputs

    if conversion_errors:

        def as_nested_dict(nested_dd):
            return {
                key: (as_nested_dict(value) if isinstance(value, dict) else value) for key, value in nested_dd.items()
            }

        conversion_errors = as_nested_dict(conversion_errors)
        raise UnconvertibleError(conversion_errors)

    del data["prediction"]
    if "training" in data:
        del data["training"]

    return data


def convert_model_v0_3_1_to_v0_3_2(data: Dict[str, Any]) -> Dict[str, Any]:
    data["type"] = "model"
    data["format_version"] = "0.3.2"
    future = data.get("config", {}).get("future", {}).pop("0.3.2", {})

    # authors
    data["authors"] = [{"name": name} for name in data["authors"]]
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
    for weights_format, weights_entry in data["weights"].items():
        if "authors" not in weights_entry:
            continue

        weights_entry["authors"] = [{"name": name} for name in weights_entry["authors"]]
        authors_update = future.get("weights", {}).get(weights_format, {}).get("authors")
        if authors_update is not None:
            for a, u in zip(weights_entry["authors"], authors_update):
                a.update(u)

    # documentation: we now enforce `documentation` to be a local md file
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
            data["config"][AUTO_CONVERTED_DOCUMENTATION_FILE_NAME] = data["documentation"]
            data["documentation"] = AUTO_CONVERTED_DOCUMENTATION_FILE_NAME

    return data


def _maybe_convert_model(data: Dict[str, Any]) -> Dict[str, Any]:
    """auto converts model 'data' to newest format"""
    if data.get("format_version", "0.1.0") == "0.1.0":
        data = convert_model_from_v0_1(data)

    if data["format_version"] == "0.3.0":
        # no breaking change, bump to 0.3.1
        data["format_version"] = "0.3.1"

    if data["format_version"] == "0.3.1":
        data = convert_model_v0_3_1_to_v0_3_2(data)

    # remove 'future' from config if no other than the used future entries exist
    config = data.get("config", {})
    if config.get("future") == {}:
        del config["future"]

    # remove 'config' if now empty
    if data.get("config") == {}:
        del data["config"]

    return data


def maybe_convert(data: Dict[str, Any]) -> Dict[str, Any]:
    type_ = data.get("type") or data.get("config", {}).get("future", {}).get("type", "model")
    if type_ == "model":
        return _maybe_convert_model(data)
    else:
        return data
