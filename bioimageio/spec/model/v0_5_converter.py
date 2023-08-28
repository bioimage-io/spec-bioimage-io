import collections.abc
from typing import Any, Dict, List, Mapping, Sequence, Union

from bioimageio.spec._internal.constants import ALERT
from bioimageio.spec._internal.field_validation import ValContext
from bioimageio.spec.generic.v0_3_converter import convert_attachments
from bioimageio.spec.model import v0_4_converter
from bioimageio.spec.types import RawStringDict, RawValue


def convert_from_older_format(data: RawStringDict, context: ValContext):
    fv = data.get("format_version")
    if not isinstance(fv, str) or fv.count(".") != 2:
        return

    v0_4_converter.convert_from_older_format(data, context)
    major, minor = map(int, fv.split(".")[:2])

    if (major, minor) > (0, 5):
        return

    if minor == 4:
        _convert_model_from_v0_4_to_0_5_0(data, context)


def _convert_model_from_v0_4_to_0_5_0(data: RawStringDict, context: ValContext) -> None:
    _convert_axes_string_to_axis_descriptions(data, context=context)
    _convert_architecture(data)
    convert_attachments(data)
    _ = data.pop("download_url", None)

    if (p := data.get("parent")) and isinstance(p, dict) and "uri" in p:
        p["rdf_source"] = p.pop("uri")

    data["format_version"] = "0.5.0"


def _convert_axes_string_to_axis_descriptions(data: RawStringDict, *, context: ValContext):
    inputs = data.get("inputs")
    outputs = data.get("outputs")
    sample_inputs = data.pop("sample_inputs", None)
    sample_outputs = data.pop("sample_outputs", None)
    test_inputs = data.pop("test_inputs", None)
    test_outputs = data.pop("test_outputs", None)

    if isinstance(inputs, collections.abc.Sequence):
        data["inputs"] = list(inputs)
        _update_tensor_specs(data["inputs"], test_inputs, sample_inputs, context=context)

    if isinstance(outputs, collections.abc.Sequence):
        data["outputs"] = list(outputs)
        _update_tensor_specs(data["outputs"], test_outputs, sample_outputs, context=context)


def _update_tensor_specs(
    tensor_data: List[RawValue],
    test_tensors: Any,
    sample_tensors: Any,
    *,
    context: ValContext,
):
    tts: Sequence[Any] = test_tensors if isinstance(test_tensors, collections.abc.Sequence) else ()
    sts: Sequence[Any] = sample_tensors if isinstance(sample_tensors, collections.abc.Sequence) else ()

    for idx in range(len(tensor_data)):
        d = tensor_data[idx]
        if not isinstance(d, dict):
            continue

        reordered_shape = _reorder_tensor_shape(d.get("shape"))
        new_d = {}
        for keep in ("name", "description"):
            if keep in d:
                new_d[keep] = d[keep]

        if len(tts) > idx:
            new_d["test_tensor"] = tts[idx]

        if len(sts) > idx:
            new_d["sample_tensor"] = sts[idx]

        new_d["data"] = dict(type="float32")

        if isinstance(d["axes"], str):
            new_axes = [
                _get_axis_description_from_letter(a, reordered_shape.get(i), context=context)
                for i, a in enumerate(d["axes"])
            ]
            new_d["axes"] = new_axes

        for proc in ("preprocessing", "postprocessing"):
            if (
                isinstance(p := d.get(proc), dict)
                and isinstance(p_kwargs := p.get("kwargs"), dict)
                and isinstance(p_kwargs_axes := p_kwargs.get("axes"), str)
            ):
                p_axes = [_get_axis_description_from_letter(a, context=context) for a in p_kwargs_axes]
                p_kwargs["axes"] = [a.get("name", a["type"]) for a in p_axes]

        tensor_data[idx] = new_d


def _reorder_tensor_shape(orig_shape: Union[Any, Sequence[Any], Mapping[Any, Any]]) -> Dict[int, Any]:
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
                i: dict(offset=offset.get(i, 0), scale=scale.get(i, 1), reference=orig_shape["reference_tensor"])
                for i in range(max(len(offset), len(scale)))
            }
        else:
            m: Sequence[Any] = _m if isinstance(_m := orig_shape.get("min"), collections.abc.Sequence) else []
            s: Sequence[Any] = _s if isinstance(_s := orig_shape.get("step"), collections.abc.Sequence) else []
            return {i: dict(min=mm, step=ss) for i, (mm, ss) in enumerate(zip(m, s))}
    elif isinstance(orig_shape, collections.abc.Sequence):
        return {i: s for i, s in enumerate(orig_shape)}

    return {}


def _get_axis_description_from_letter(
    letter: str, size: Union[int, Dict[str, Any], None] = None, *, context: ValContext
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
    axis: Dict[str, Any] = dict(type=AXIS_TYPE_MAP.get(letter, letter))
    if axis["type"] == "space":
        axis["name"] = letter

    if size is None or axis["type"] == "batch":
        return axis

    if not isinstance(size, int):
        scale = 1
        if "scale" in size:
            scale = size.pop("scale")
            if axis["type"] == "channel":
                if scale != 1.0 and ALERT >= context["warning_level"]:
                    raise ValueError("Channel axis referenced with scale != 1")
            elif scale is not None:
                axis["scale"] = scale

        if "reference" in size:
            if scale is None:  # old way to insert a new axis dimension
                size = size.get("offset", 0)  # 0 is invalid on purpose
            else:
                size["reference"] = f"{size['reference']}.{axis.get('name', axis['type'])}"
                if ALERT >= context["warning_level"]:
                    raise ValueError(
                        f"Converting tensor shape: we assume axis '{axis['name']}' of tensor and reference match."
                    )

        if isinstance(size, dict) and "min" in size and size.get("step") == 0:
            size = size["min"]

    axis["size"] = size

    return axis


def _convert_architecture(data: Dict[str, Any]) -> None:
    weights: "Any | Dict[str, Any]" = data.get("weights")
    if not isinstance(weights, dict):
        return

    state_dict_entry: "Any | Dict[str, Any]" = weights.get("pytorch_state_dict")
    if not isinstance(state_dict_entry, dict):
        return

    callable_: Union[Any, Dict[Any, Any]] = state_dict_entry.pop("architecture", None)
    if not isinstance(callable_, dict):
        return

    if (src_file := callable_.pop("source_file", None)) is not None:
        callable_["file"] = src_file

    state_dict_entry["architecture"] = dict(callable=callable_)
    if sha := state_dict_entry.pop("architecture_sha256", None):
        state_dict_entry["architecture"]["sha256"] = sha

    if kwargs := state_dict_entry.pop("kwargs", None):
        state_dict_entry["architecture"]["kwargs"] = kwargs
