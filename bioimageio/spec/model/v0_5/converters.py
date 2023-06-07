from typing import Any, Dict

from bioimageio.spec.model.v0_4.converters import maybe_convert as maybe_convert_v04


def maybe_convert(data: Dict[str, Any]) -> Dict[str, Any]:
    """auto converts model 'data' to newest format"""
    data = maybe_convert_v04(data)
    assert "format_version" in data
    major, minor, patch = map(int, data["format_version"].split("."))
    if (major, minor) > (0, 5):
        return data

    if minor == 4:
        data = convert_model_from_v0_4_to_0_5_0(data)

    return data


def convert_model_from_v0_4_to_0_5_0(data: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(data)

    # convert axes string to axis descriptions
    inputs = data.get("inputs")
    outputs = data.get("outputs")
    test_inputs = data.get("test_inputs")
    test_outputs = data.get("test_outputs")
    sample_inputs = data.get("sample_inputs")
    sample_outputs = data.get("sample_outputs")

    axis_letter_map = {"t": "time", "c": "channel", "i": "index"}

    def convert_axes(tensor_spec):
        axes = tensor_spec.get("axes")
        if isinstance(axes, str):
            tensor_spec["axes"] = [dict(role=axis_letter_map.get(a, a)) for a in axes]

    def update_tensor_specs(tensor_specs, test_tensors, sample_tensors):
        for i, param in enumerate(tensor_specs):
            if not isinstance(param, dict):
                continue

            convert_axes(param)
            if isinstance(test_tensors, list) and len(test_tensors) == len(inputs):
                param["test_tensor"] = test_tensors[i]

            if isinstance(sample_tensors, list) and len(sample_tensors) == len(inputs):
                param["sample_tensor"] = sample_tensors[i]

    if isinstance(inputs, list):
        update_tensor_specs(inputs, test_inputs, sample_inputs)

    if isinstance(outputs, list):
        update_tensor_specs(outputs, test_outputs, sample_outputs)

    data["format_version"] = "0.5.0"
    return data
