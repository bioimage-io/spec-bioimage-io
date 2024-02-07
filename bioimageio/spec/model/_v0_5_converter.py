import collections.abc
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from bioimageio.spec._internal.constants import ALERT
from bioimageio.spec._internal.field_warning import issue_warning
from bioimageio.spec._internal.types import BioimageioYamlContent, YamlKey, YamlValue
from bioimageio.spec.generic.v0_3_converter import convert_attachments


def convert_model_data_from_v0_4_to_0_5_0(data: BioimageioYamlContent) -> None:
    _convert_axes_string_to_axis_descriptions(data)
    _convert_architecture(data)
    convert_attachments(data)
    _convert_weights(data)
    _ = data.pop("download_url", None)
    _ = data.pop("rdf_source", None)

    if isinstance(data.get("parent"), dict):
        _ = data.pop("parent")

    data["format_version"] = "0.5.0"


def _convert_axes_string_to_axis_descriptions(data: BioimageioYamlContent):
    inputs = data.get("inputs")
    outputs = data.get("outputs")
    sample_inputs = data.pop("sample_inputs", None)
    sample_outputs = data.pop("sample_outputs", None)
    test_inputs = data.pop("test_inputs", None)
    test_outputs = data.pop("test_outputs", None)

    if isinstance(inputs, collections.abc.Sequence):
        data["inputs"] = list(inputs)
        _update_tensor_specs(data["inputs"], test_inputs, sample_inputs)

    if isinstance(outputs, collections.abc.Sequence):
        data["outputs"] = list(outputs)
        _update_tensor_specs(data["outputs"], test_outputs, sample_outputs)


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
                get_axis_description_from_letter(a, reordered_shape.get(i), halo=halo.get(i))
                for i, a in enumerate(d["axes"])
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

                p_axes = [get_axis_description_from_letter(a, halo=None) for a in p_kwargs_axes]
                if p.get("id") == "zero_mean_unit_variance" and p_kwargs.get("mode") == "fixed":
                    p["id"] = "fixed_zero_mean_unit_variance"
                    _ = p_kwargs.pop("axes", None)
                else:
                    p_kwargs["axes"] = [a.get("id", a["type"]) for a in p_axes]

                if p_kwargs.get("mode") == "per_dataset" and isinstance(p_kwargs["axes"], list):
                    p_kwargs["axes"] = ["batch"] + p_kwargs["axes"]

        tensor_data[idx] = new_d


def analyze_tensor_shape(orig_shape: Union[Any, Sequence[Any], Mapping[Any, Any]]) -> Dict[int, Any]:
    if isinstance(orig_shape, collections.abc.Mapping):
        if "reference_tensor" in orig_shape:
            x: Union[Any, Sequence[Any]]
            if isinstance(x := orig_shape.get("offset"), collections.abc.Sequence):
                offset: Dict[int, float] = {i: 2 * xx if isinstance(xx, (int, float)) else xx for i, xx in enumerate(x)}
            else:
                offset = {}
            if isinstance(x := orig_shape.get("scale"), collections.abc.Sequence):
                scale: Dict[int, Any] = dict(enumerate(x))
            else:
                scale = {}

            return {
                i: dict(offset=offset.get(i, 0), scale=1 / scale.get(i, 1), reference=orig_shape["reference_tensor"])
                for i in range(max(len(offset), len(scale)))
            }
        else:
            m: Sequence[Any] = _m if isinstance(_m := orig_shape.get("min"), collections.abc.Sequence) else []
            s: Sequence[Any] = _s if isinstance(_s := orig_shape.get("step"), collections.abc.Sequence) else []
            return {i: dict(min=mm, step=ss) for i, (mm, ss) in enumerate(zip(m, s))}
    elif isinstance(orig_shape, collections.abc.Sequence):
        return {i: s for i, s in enumerate(orig_shape)}

    return {}


def get_axis_description_from_letter(
    letter: str,
    size: Union[int, Dict[YamlKey, YamlValue], None] = None,
    *,
    halo: Optional[Any],
):
    AXIS_TYPE_MAP = {
        "b": "batch",
        "t": "time",
        "i": "index",
        "c": "channel",
        "x": "space",
        "y": "space",
        "z": "space",
    }
    axis: Dict[YamlKey, YamlValue] = dict(type=AXIS_TYPE_MAP.get(letter, letter))
    if axis["type"] == "space":
        axis["id"] = letter

    if size is None or axis["type"] == "batch":
        return axis

    if not isinstance(size, int):
        scale = 1
        size = dict(size)
        if "scale" in size:
            scale = size.pop("scale")
            if axis["type"] == "channel":
                if scale != 1.0:
                    issue_warning("Channel axis referenced with scale != 1", value=scale, severity=ALERT)
            elif scale is not None:
                axis["scale"] = scale

        if "reference" in size:
            if scale is None:  # old way to insert a new axis dimension
                offset = size.get("offset", 0)  # 0 is invalid on purpose
                assert isinstance(offset, int)
                size = offset
            else:
                size["tensor_id"] = size.pop("reference")
                size["axis_id"] = axis.get("id", axis["type"])
                issue_warning(
                    "Converting tensor shape: we assume axis '{value}' of tensor and reference to match.",
                    value=size["axis_id"],
                    severity=ALERT,
                )

        if isinstance(size, dict) and "min" in size and size.get("step") == 0:
            min_size = size["min"]
            assert isinstance(min_size, int)
            size = min_size

    axis["size"] = size
    if halo is not None:
        if halo or axis["type"] in ("time", "space"):  # ignore zero halo for non-time/space axes
            axis["halo"] = halo

    return axis


def _convert_architecture(data: Dict[str, Any]) -> None:
    weights: "Any | Dict[str, Any]" = data.get("weights")
    if not isinstance(weights, dict):
        return

    state_dict_entry: "Any | Dict[str, Any]" = weights.get("pytorch_state_dict")
    if not isinstance(state_dict_entry, dict):
        return

    arch: Any = state_dict_entry.pop("architecture", None)
    if isinstance(arch, str):
        if arch.startswith("http") and arch.count(":") == 2:
            http, source, callable_ = arch.split(":")
            arch = dict(source=":".join((http, source)), callable=callable_)
        elif not arch.startswith("http") and arch.count(":") == 1:
            source, callable_ = arch.split(":")
            arch = dict(source=source, callable=callable_)
        elif "." in arch:
            *mods, callable_ = arch.split(".")
            import_from = ".".join(mods)
            arch = dict(import_from=import_from, callable=callable_)
        else:
            arch = dict(callable=arch)  # will throw validation error
    elif not isinstance(arch, dict):
        arch = dict(callalbe=arch)

    if sha := state_dict_entry.pop("architecture_sha256", None):
        arch["sha256"] = sha

    if kwargs := state_dict_entry.pop("kwargs", None):
        arch["kwargs"] = kwargs

    state_dict_entry["architecture"] = arch

    deps = state_dict_entry.get("dependencies", None)
    if isinstance(deps, str):
        if deps.startswith("conda:"):
            deps = deps[len("conda:") :]

        state_dict_entry["dependencies"] = dict(source=deps)