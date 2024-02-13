import collections.abc
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from bioimageio.spec._internal.constants import ALERT
from bioimageio.spec._internal.field_warning import issue_warning
from bioimageio.spec._internal.types import BioimageioYamlContent, YamlKey, YamlValue
from bioimageio.spec.generic._v0_3_converter import convert_attachments
from bioimageio.spec.model import v0_4


def _convert_weights(data: BioimageioYamlContent):
    if "weights" in data and isinstance((weights := data["weights"]), dict):
        for weights_name in ("pytorch_state_dict", "torchscript"):
            entry = weights.get(weights_name)
            if not isinstance(entry, dict):
                continue

            entry["pytorch_version"] = entry.get("pytorch_version", "1.10")

        for weights_name in ("keras_hdf5", "tensorflow_saved_model_bundle", "tensorflow_js"):
            entry = weights.get(weights_name)
            if not isinstance(entry, dict):
                continue

            entry["tensorflow_version"] = entry.get("tensorflow_version", "1.15")
            deps = entry.pop("dependencies", None)
            if deps is None:
                pass
            elif isinstance(deps, str) and deps.startswith("conda:"):
                entry["dependencies"] = dict(source=deps[len("conda:") :])
            else:
                entry["dependencies"] = dict(source=deps)

        entry = weights.get("onnx")
        if isinstance(entry, dict):
            entry["opset_version"] = entry.get("opset_version", 15)


def _update_tensor_specs(
    tensor_data: List[YamlValue],
    test_tensors: Any,
    sample_tensors: Any,
):
    tts: Sequence[Any] = test_tensors if isinstance(test_tensors, collections.abc.Sequence) else ()
    sts: Sequence[Any] = sample_tensors if isinstance(sample_tensors, collections.abc.Sequence) else ()

    for idx in range(len(tensor_data)):
        d = tensor_data[idx]
        if not isinstance(d, dict):
            continue

        reordered_shape = analyze_tensor_shape(d.get("shape"))
        new_d: Dict[YamlKey, YamlValue] = {}
        if "name" in d:
            new_d["id"] = d["name"]

        if "description" in d:
            new_d["description"] = d["description"]

        if len(tts) > idx:
            new_d["test_tensor"] = dict(source=tts[idx])

        if len(sts) > idx:
            new_d["sample_tensor"] = dict(source=sts[idx])

        new_d["data"] = dict(type=d.get("data_type", "float32"))

        halo_seq = d.get("halo")
        if isinstance(halo_seq, (list, tuple)):
            halo = {i: h for i, h in enumerate(halo_seq)}
        else:
            halo = {}

        if isinstance(d["axes"], str):
            new_axes: List[YamlValue] = [
                convert_axes(a, reordered_shape.get(i), halo=halo.get(i)) for i, a in enumerate(d["axes"])
            ]
            new_d["axes"] = new_axes

        for proc in ("preprocessing", "postprocessing"):
            if (
                isinstance(p := d.get(proc), dict)
                and isinstance(p_kwargs := p.get("kwargs"), dict)
                and isinstance(p_kwargs_axes := p_kwargs.get("axes"), str)
            ):
                if "name" in p_kwargs:
                    p_kwargs["id"] = p_kwargs.pop("name")

                p_axes = [convert_axes(a, halo=None) for a in p_kwargs_axes]
                if p.get("id") == "zero_mean_unit_variance" and p_kwargs.get("mode") == "fixed":
                    p["id"] = "fixed_zero_mean_unit_variance"
                    _ = p_kwargs.pop("axes", None)
                else:
                    p_kwargs["axes"] = [a.get("id", a["type"]) for a in p_axes]

                if p_kwargs.get("mode") == "per_dataset" and isinstance(p_kwargs["axes"], list):
                    p_kwargs["axes"] = ["batch"] + p_kwargs["axes"]

        tensor_data[idx] = new_d
