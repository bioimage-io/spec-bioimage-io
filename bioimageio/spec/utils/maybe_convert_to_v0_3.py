import copy
import warnings
from collections import defaultdict
from typing import Any, Dict

from bioimageio.spec import schema_v0_1
from bioimageio.spec.exceptions import PyBioUnconvertibleException


def convert_model_from_v0_1(data: Dict[str, Any]) -> Dict[str, Any]:
    schema_v0_1.Model().validate(data)

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
    weights_future = future.pop("weights", {})
    weights_entry = {
        # "id": weights_future.pop("id", "default"),
        # "name": weights_future.pop("name", "default weights"),
        # "description": weights_future.pop("description", "description"),
        # "authors": data["authors"],
        "source": source,
        "sha256": sha256,
        # "tags": weights_future.pop("tags", []),
    }

    data["weights"] = {weights_format: weights_entry}

    if conversion_errors:

        def as_nested_dict(nested_dd):
            return {
                key: (as_nested_dict(value) if isinstance(value, dict) else value) for key, value in nested_dd.items()
            }

        conversion_errors = as_nested_dict(conversion_errors)
        raise PyBioUnconvertibleException(conversion_errors)

    del data["prediction"]
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

    return data


def maybe_convert_model_to_v0_3(data: Dict[str, Any]) -> Dict[str, Any]:

    if data.get("format_version", "0.1.0") == "0.1.0":
        data = convert_model_from_v0_1(data)

    if data["format_version"] == "0.3.0":
        # no breaking change, bump to 0.3.1
        data["format_version"] = "0.3.1"

    if data["format_version"] == "0.3.1":
        data = convert_model_v0_3_1_to_v0_3_2(data)

    return data
