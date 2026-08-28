import warnings
from functools import singledispatch
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union

from typing_extensions import NotRequired, TypedDict

from bioimageio.spec._internal.io_utils import download, load_array
from bioimageio.spec._internal.types import FileName, FileSource
from bioimageio.spec.model import v0_4, v0_5

MacroId = Literal["binarize", "scale_linear", "scale_range", "zero_mean_unit_variance", "fixed_zero_mean_unit_variance"]
MacroFileName = Literal[
    "binarize.ijm",
    "scale_linear.ijm",
    "per_sample_scale_range.ijm",
    "fixed_zero_mean_unit_variance.ijm",
    "zero_mean_unit_variance.ijm",
]


class DeepImageJProc_Config(TypedDict):
    spec: Optional[Literal["ij.IJ::runMacroFile"]]
    kwargs: NotRequired[MacroFileName]


DeepImageJ_Config = Dict[str, Any]

ConfigWithDeepImageJ_Config = Dict[str, Union[DeepImageJProc_Config, Any]]
MacroFileContent = str


def dij_warning(msg: str):
    warnings.warn(f"DeepImageJ: {msg}")


@singledispatch
def _get_deepimagej_macro(
    proc: type,
) -> Tuple[DeepImageJProc_Config, MacroFileName, MacroFileContent]:
    raise TypeError(f"Invalid processing description {type(proc)}")


@_get_deepimagej_macro.register
def _(
    proc: Union[v0_4.PreprocessingDescr, v0_4.PostprocessingDescr]
) -> Tuple[DeepImageJProc_Config, MacroFileName, MacroFileContent]:
    raise NotImplementedError(f"Macro {proc.name} is not available")


@_get_deepimagej_macro.register
def _(
    proc: Union[v0_5.PreprocessingDescr, v0_5.PostprocessingDescr]
) -> Tuple[DeepImageJProc_Config, MacroFileName, MacroFileContent]:
    raise NotImplementedError(f"Macro {proc.id} is not available")


@_get_deepimagej_macro.register
def _(proc: v0_4.ScaleLinearDescr) -> Tuple[DeepImageJProc_Config, MacroFileName, MacroFileContent]:
    if proc.kwargs.axes is not None:
        raise NotImplementedError("DeepImageJ Macro 'scale_linear.ijm' with axes.")

    return _format_macro("scale_linear.ijm", replace={"gain": proc.kwargs.gain, "offset": proc.kwargs.offset})


@_get_deepimagej_macro.register
def _(proc: v0_5.ScaleLinearDescr) -> Tuple[DeepImageJProc_Config, MacroFileName, MacroFileContent]:
    if proc.kwargs.axis is not None:
        raise NotImplementedError("DeepImageJ Macro 'scale_linear.ijm' with axis.")

    return _format_macro("scale_linear.ijm", replace={"gain": proc.kwargs.gain, "offset": proc.kwargs.offset})


@_get_deepimagej_macro.register
def _(
    proc: Union[v0_4.ScaleRangeDescr, v0_5.ScaleRangeDescr]
) -> Tuple[DeepImageJProc_Config, MacroFileName, MacroFileContent]:
    dij_warning(f"ignoring axes kwarg {proc.kwargs.axes}")
    dij_warning(f"ignoring eps kwarg {proc.kwargs.eps}")

    return _format_macro(
        "per_sample_scale_range.ijm",
        replace={"min_precentile": proc.kwargs.min_percentile, "max_percentile": proc.kwargs.max_percentile},
    )


@_get_deepimagej_macro.register
def _(proc: v0_5.FixedZeroMeanUnitVarianceDescr) -> Tuple[DeepImageJProc_Config, MacroFileName, MacroFileContent]:
    if proc.kwargs.axis is not None:
        raise NotImplementedError("DeepImageJ Macro 'fixed_zero_mean_unit_variance.ijm; with axis not implemented")

    return _format_macro(
        "fixed_zero_mean_unit_variance.ijm", replace={"paramMean": proc.kwargs.mean, "paramStd": proc.kwargs.std}
    )


@_get_deepimagej_macro.register
def _(proc: v0_4.ZeroMeanUnitVarianceDescr) -> Tuple[DeepImageJProc_Config, MacroFileName, MacroFileContent]:
    dij_warning(f"ignoring axes kwarg {proc.kwargs.axes}")
    dij_warning(f"ignoring eps kwarg {proc.kwargs.eps}")
    if proc.kwargs.mode == "fixed":
        return _format_macro(
            "fixed_zero_mean_unit_variance.ijm", replace={"paramMean": proc.kwargs.mean, "paramStd": proc.kwargs.std}
        )

    return _format_macro("zero_mean_unit_variance.ijm", replace={})


@_get_deepimagej_macro.register
def _(
    proc: Union[v0_4.BinarizeDescr, v0_5.BinarizeDescr]
) -> Tuple[DeepImageJProc_Config, MacroFileName, MacroFileContent]:
    return _format_macro("binarize.ijm", replace={"optimalThreshold": proc.kwargs.threshold})


def _format_macro(
    macro: MacroFileName, replace: Dict[str, Any]
) -> Tuple[DeepImageJProc_Config, MacroFileName, MacroFileContent]:
    original_macro = download(
        f"https://raw.githubusercontent.com/deepimagej/imagej-macros/master/bioimage.io/{macro}"
    ).path.read_text()

    # replace the kwargs in the macro file
    if replace:
        lines = []
        for line in original_macro.split("\n"):
            kwarg_candidates = [kwarg for kwarg in replace if line.startswith(kwarg)]
            if kwarg_candidates:
                assert len(kwarg_candidates) == 1
                kwarg = kwarg_candidates[0]
                # each kwarg should only be replaced ones
                val = replace.pop(kwarg)
                lines.append(f"{kwarg} = {val};\n")
            else:
                lines.append(line)

        macro_content: MacroFileContent = "\n".join(lines)
    else:
        macro_content: MacroFileContent = original_macro

    return {"spec": "ij.IJ::runMacroFile", "kwargs": macro}, macro, macro_content


def build_deepimagej_config(
    model: Union[v0_4.ModelDescr, v0_5.ModelDescr],
) -> Tuple[ConfigWithDeepImageJ_Config, Dict[FileName, MacroFileContent]]:  # type: ignore
    if len(model.inputs) != 1 or len(model.outputs) != 1:
        raise ValueError("deepimagej config only valid for single input/output")

    attachments: Dict[FileName, MacroFileContent] = {}
    ipt = model.inputs[0]
    tensor_id = ipt.name if isinstance(ipt, v0_4.InputTensorDescr) else ipt.id

    if len(ipt.preprocessing) == 0:
        preprocess_ij: List[DeepImageJProc_Config] = [{"spec": None}]
    elif len(ipt.preprocessing) == 1:
        preprocess_ij = []
        for p in ipt.preprocessing:
            dij_proc_config, macro_file_name, macro_content = _get_deepimagej_macro(p)
            preprocess_ij.append(dij_proc_config)
            attachments[f"{tensor_id}_{macro_file_name}"] = macro_content

    else:
        raise ValueError("deepimagej does not support multiple preprocesing steps for one input tensor")

    out = model.outputs[0]
    if len(out.postprocessing) == 0:
        postprocess_ij: List[DeepImageJProc_Config] = [{"spec": None}]
    elif len(out.postprocessing) == 1:
        postprocess_ij = []
        for p in out.postprocessing:
            dij_proc_config, macro_file_name, macro_content = _get_deepimagej_macro(p)
            postprocess_ij.append(dij_proc_config)
            attachments[f"{tensor_id}_{macro_file_name}"] = macro_content

    else:
        raise ValueError("deepimagej does not support multiple postprocesing steps for one output tensor")

    def get_test_tensor_size(test_tensor_source: FileSource, axes: Sequence[v0_4.AxesStr]):  # type: ignore
        shape = load_array(test_tensor_source).shape
        assert len(shape) == len(axes)
        shape = [sh for sh, ax in zip(shape, axes) if ax != "b"]
        axes = [ax for ax in axes if ax != "b"]
        # the shape for deepij is always given as xyzc
        if len(shape) == 3:
            axes_ij = "xyc"
        else:
            axes_ij = "xyzc"
        assert set(axes) == set(axes_ij)
        axis_permutation = [axes_ij.index(ax) for ax in axes]
        shape = [shape[permut] for permut in axis_permutation]
        if len(shape) == 3:
            shape = shape[:2] + [1] + shape[-1:]
        assert len(shape) == 4
        return " x ".join(map(str, shape))

    # TODO: finish implementation
    # # deepimagej always expexts a pixel size for the z axis
    # pixel_sizes_ = [pix_size if "z" in pix_size else dict(z=1.0, **pix_size) for pix_size in pixel_sizes]

    # test_info = {
    #     "inputs": [
    #         {"name": in_path, "size": get_test_tensor_size(in_path, axes), "pixel_size": pix_size}
    #         for in_path, axes, pix_size in zip(test_inputs, input_axes, pixel_sizes_)
    #     ],
    #     "outputs": [
    #         {"name": out_path, "type": "image", "size": get_test_tensor_size(out_path, axes)}
    #         for out_path, axes in zip(test_outputs, output_axes)
    #     ],
    #     "memory_peak": None,
    #     "runtime": None,
    # }

    # config = {
    #     "prediction": {"preprocess": preprocess_ij, "postprocess": postprocess_ij},
    #     "test_information": test_info,
    #     # other stuff deepimagej needs
    #     "pyramidal_model": False,
    #     "allow_tiling": True,
    #     "model_keys": None,
    # }
    # return {"deepimagej": config}, [Path(a) for a in attachments]
