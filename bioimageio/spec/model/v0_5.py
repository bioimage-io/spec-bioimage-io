import collections
from typing import Annotated, Any, Dict, List, Literal, Optional, Set, Tuple, Union, get_args

from annotated_types import MaxLen, MinLen
from pydantic import AfterValidator, AllowInfNan, FieldValidationInfo, field_validator, model_validator

from bioimageio.spec._internal._constants import SI_UNIT_REGEX
from bioimageio.spec._internal._utils import Field
from bioimageio.spec.shared.nodes import Node
from bioimageio.spec.shared.types import Identifier, RawMapping

from . import v0_4

LatestFormatVersion = Literal["0.5.0"]
FormatVersion = Literal[LatestFormatVersion]


LATEST_FORMAT_VERSION: LatestFormatVersion = get_args(LatestFormatVersion)[0]

# unit names from https://ngff.openmicroscopy.org/latest/#axes-md
SpaceUnit = Literal[
    "angstrom",
    "attometer",
    "centimeter",
    "decimeter",
    "exameter",
    "femtometer",
    "foot",
    "gigameter",
    "hectometer",
    "inch",
    "kilometer",
    "megameter",
    "meter",
    "micrometer",
    "mile",
    "millimeter",
    "nanometer",
    "parsec",
    "petameter",
    "picometer",
    "terameter",
    "yard",
    "yoctometer",
    "yottameter",
    "zeptometer",
    "zettameter",
]

TimeUnit = Literal[
    "attosecond",
    "centisecond",
    "day",
    "decisecond",
    "exasecond",
    "femtosecond",
    "gigasecond",
    "hectosecond",
    "hour",
    "kilosecond",
    "megasecond",
    "microsecond",
    "millisecond",
    "minute",
    "nanosecond",
    "petasecond",
    "picosecond",
    "second",
    "terasecond",
    "yoctosecond",
    "yottasecond",
    "zeptosecond",
    "zettasecond",
]

AxisType = Literal["batch", "channel", "index", "time", "space"]
ShortId = Annotated[Identifier, MaxLen(16)]
SAME_AS_TYPE = "<same as type>"


# this Axis definition is compatible with the NGFF draft from July 10, 2023
# https://ngff.openmicroscopy.org/latest/#axes-md
class AxisBase(Node):
    name: Union[ShortId, List[ShortId]] = SAME_AS_TYPE
    """a unique name"""
    description: Annotated[str, MaxLen(128)] = ""
    # unit: Union[SpaceUnit, TimeUnit, ShortId, Tuple[ShortId, ...], None] = None
    # step: Annotated[int, Gt(0)] = 1

    @field_validator("name", mode="after")
    @classmethod
    def set_default_name(cls, value: str, info: FieldValidationInfo) -> str:
        if value == SAME_AS_TYPE and isinstance(info.data["type"], str):
            return info.data["type"]
        else:
            return value


class BatchAxis(AxisBase):
    type: Literal["batch"] = "batch"


MeasurementScale = Literal["nominal", "ordinal", "interval", "ratio"]


class ChannelAxis(AxisBase):
    type: Literal["channel"] = "channel"
    value_scale: Union[MeasurementScale, Tuple[MeasurementScale, ...]]
    value_unit: Annotated[str, AfterValidator(lambda s: s.replace("×", "·").replace("*", "·"))] = Field(
        pattern=SI_UNIT_REGEX, examples=["lx·s"]
    )
    """(composed) SI unit"""


class IndexAxis(AxisBase):
    type: Literal["index"] = "index"


class TimeAxis(AxisBase):
    type: Literal["time"] = "time"


class SpaceAxis(AxisBase):
    type: Literal["space"] = "space"
    name: ShortId = Field("x", examples=["x", "y", "z"])


Axis = Annotated[Union[BatchAxis, ChannelAxis, IndexAxis, TimeAxis, SpaceAxis], Field(discriminator="type")]


class TensorBase(Node):
    name: Identifier  # todo: validate duplicates
    """Tensor name. No duplicates are allowed."""

    description: str = ""
    """Brief descripiton of the tensor"""

    axes: Tuple[Axis, ...]

    data_type: str
    """The data type of this tensor."""

    data_range: Optional[Tuple[Annotated[float, AllowInfNan(True)], Annotated[float, AllowInfNan(True)]]] = None
    """Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
    If not specified, the full data range that can be expressed in `data_type` is allowed."""

    @field_validator("axes", mode="after")
    @classmethod
    def validate_axes(cls, axes: Tuple[Axis, ...]):
        seen: Set[str] = set()
        duplicate_axes_names: Set[str] = set()
        for a in axes:
            axis_name = a.name if isinstance(a.name, str) else ",".join(a.name)
            (duplicate_axes_names if axis_name in seen else seen).add(axis_name)

        if duplicate_axes_names:
            raise ValueError(f"Duplicate axis names: {duplicate_axes_names}")

        return axes


class InputTensor(TensorBase):
    data_type: Literal["float32"]
    """For now an input tensor is expected to be given as `float32`.
    The data flow in bioimage.io models is explained
    [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit)."""

    # shape: Union[Tuple[int, ...], v0_4.ParametrizedInputShape] = Field(
    #     examples=[(1, 512, 512, 1), dict(min=(1, 64, 64, 1), step=(0, 32, 32, 0))]
    # )
    # """Specification of input tensor shape."""

    preprocessing: Tuple[v0_4.Preprocessing, ...] = ()
    """Description of how this input should be preprocessed."""

    @model_validator(mode="after")
    def validate_preprocessing_kwargs(self):
        axes_names = [a.name for a in self.axes]
        for p in self.preprocessing:
            kwarg_axes = p.kwargs.get("axes", ())
            if any(a not in axes_names for a in kwarg_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes names")

        return self


class OutputTensor(TensorBase):
    data_type: Literal["float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64"]
    """Data type.
    The data flow in bioimage.io models is explained
    [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit)."""

    # shape: Union[Tuple[int, ...], v0_4.ImplicitOutputShape]
    # """Output tensor shape."""

    # halo: Optional[Tuple[int, ...]] = None
    # """The `halo` that should be cropped from the output tensor to avoid boundary effects.
    # The `halo` is to be cropped from both sides, i.e. `shape_after_crop = shape - 2 * halo`.
    # To document a `halo` that is already cropped by the model `shape.offset` has to be used instead."""

    postprocessing: Tuple[v0_4.Postprocessing, ...] = ()
    """Description of how this output should be postprocessed."""

    # @model_validator(mode="after")
    # def matching_halo_length(self):
    #     if self.halo and len(self.halo) != len(self.shape):
    #         raise ValueError(f"halo {self.halo} has to have same length as shape {self.shape}!")

    #     return self

    @model_validator(mode="after")
    def validate_postprocessing_kwargs(self):
        axes_names = [a.name for a in self.axes]
        for p in self.postprocessing:
            kwarg_axes = p.kwargs.get("axes", ())
            if any(a not in axes_names for a in kwarg_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes names")

        return self


class Model(v0_4.Model):
    """Specification of the fields used in a bioimage.io-compliant RDF to describe AI models with pretrained weights.

    These fields are typically stored in a YAML file which we call a model resource description file (model RDF).
    Like any RDF, a model RDF can be downloaded from or uploaded to the bioimage.io website and is produced or consumed
    by bioimage.io-compatible consumers (e.g. image analysis software or another website).
    """

    model_config = {
        **v0_4.Model.model_config,
        **dict(title=f"bioimage.io model RDF spec {LATEST_FORMAT_VERSION}"),
    }
    """pydantic model_config"""

    inputs: Annotated[Tuple[InputTensor, ...], MinLen(1)]
    """Describes the input tensors expected by this model."""

    outputs: Annotated[Tuple[OutputTensor, ...], MinLen(1)]
    """Describes the output tensors."""

    @classmethod
    def convert_from_older_format(cls, data: RawMapping) -> RawMapping:
        data = super().convert_from_older_format(data)
        fv = data.get("format_version")
        if not isinstance(fv, str) or fv.count(".") != 3:
            return data

        major, minor, _ = map(int, fv.split("."))
        if (major, minor) > (0, 5):
            return data

        if minor == 4:
            data = cls.convert_model_from_v0_4_to_0_5_0(data)

        return data

    @staticmethod
    def _update_v0_4_tensor_specs(
        tensor_specs: List[Union[Any, Dict[str, Any]]],
        test_tensors: Union[Any, List[Any]],
        sample_tensors: Union[Any, List[Any]],
    ) -> None:
        axis_letter_map = {"t": "time", "c": "channel", "i": "index"}

        def convert_axes(tensor_spec: Dict[str, Any]):
            axes = tensor_spec.get("axes")
            if isinstance(axes, str):
                tensor_spec["axes"] = [dict(role=axis_letter_map.get(a, a)) for a in axes]

        for i, param in enumerate(tensor_specs):
            if not isinstance(param, dict):
                continue

            convert_axes(param)
            if isinstance(test_tensors, collections.Sequence) and len(test_tensors) == len(tensor_specs):
                param["test_tensor"] = test_tensors[i]

            if isinstance(sample_tensors, collections.Sequence) and len(sample_tensors) == len(tensor_specs):
                param["sample_tensor"] = sample_tensors[i]

    @classmethod
    def convert_model_from_v0_4_to_0_5_0(cls, data: RawMapping) -> RawMapping:
        # convert axes string to axis descriptions
        data = dict(data)

        inputs = data.get("inputs")
        outputs = data.get("outputs")
        sample_inputs = data.get("sample_inputs")
        sample_outputs = data.get("sample_outputs")
        test_inputs = data.get("test_inputs")
        test_outputs = data.get("test_outputs")

        if isinstance(inputs, collections.Sequence):
            data["inputs"] = list(inputs)
            cls.update_tensor_specs(inputs, test_inputs, sample_inputs)

        if isinstance(outputs, collections.Sequence):
            data["outputs"] = list(outputs)
            cls.update_tensor_specs(outputs, test_outputs, sample_outputs)

        data["format_version"] = "0.5.0"
        return data
