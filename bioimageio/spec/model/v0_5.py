import collections.abc
from typing import Any, ClassVar, Dict, List, Literal, Mapping, Optional, Sequence, Set, Tuple, Union

from annotated_types import Ge, Gt, Interval, MaxLen
from pydantic import ConfigDict, FieldValidationInfo, HttpUrl, constr, field_validator, model_validator
from typing_extensions import Annotated, Self

from bioimageio.spec import generic
from bioimageio.spec._internal._constants import DTYPE_LIMITS, SHA256_HINT
from bioimageio.spec._internal._utils import Field
from bioimageio.spec._internal._warn import warn
from bioimageio.spec.dataset import Dataset
from bioimageio.spec.dataset.v0_3 import LinkedDataset
from bioimageio.spec.shared.nodes import Kwargs, Node
from bioimageio.spec.shared.types import (
    CapitalStr,
    Datetime,
    FileSource,
    Identifier,
    LicenseId,
    NonEmpty,
    Predicate,
    RawDict,
    RawValue,
    Sha256,
    Unit,
    Version,
)

from . import v0_4

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
OtherTensorAxisId = Annotated[constr(min_length=1, max_length=33, pattern=r"^.*\..*$"), Predicate(str.islower)]
TensorAxisId = Union[ShortId, OtherTensorAxisId]
SAME_AS_TYPE = "<same as type>"


class ParametrizedSize(Node):
    """Describes a range of valid tensor axis sizes as `size = min + n*step."""

    min: Annotated[int, Gt(0)]
    step: Annotated[int, Gt(0)]
    step_with: Optional[TensorAxisId] = None
    """name of another axis with parametrixed size to resize jointly,
    i.e. `n=n_other` for `size = min + n*step`, `size_other = min_other + n_other*step_other`.
    To step with an axis of another tensor, use `step_with = <tensor name>.<axis name>`.
    """


class SizeReference(Node):
    """A tensor axis size defined in relation to another `reference` tensor axis

    `size = reference.size / reference.scale * axis.scale + offset`
    The axis and the referenced axis need to have the same unit (or no unit).
    `scale=1.0`, if the axes have a no scale.
    """

    reference: TensorAxisId
    offset: int = 0


# this Axis definition is compatible with the NGFF draft from July 10, 2023
# https://ngff.openmicroscopy.org/latest/#axes-md
class AxisBase(Node):
    type: Literal["batch", "channel", "index", "time", "space"]

    name: ShortId
    """An axis name unique across all axes of one tensor."""

    description: Annotated[str, MaxLen(128)] = ""


class WithHalo(Node):
    halo: Annotated[int, Ge(0)] = 0
    """The halo should be cropped from the output tensor to avoid boundary effects.
    It is to be cropped from both sides, i.e. `size_after_crop = size - 2 * halo`.
    To document a halo that is already cropped by the model use `size.offset` instead."""


class BatchAxis(AxisBase):
    type: Literal["batch"] = "batch"
    name: ShortId = "batch"


class ChannelAxis(AxisBase):
    type: Literal["channel"] = "channel"
    name: ShortId = "channel"
    channel_names: Tuple[ShortId, ...] = ("channel1", "channel2", "etc")
    size: Union[Annotated[int, Gt(0)], Literal["#channel_names"]] = "#channel_names"

    def model_post_init(self, __context: Any):
        if self.size == "#channel_names":
            object.__setattr__(self, "size", len(self.channel_names))

        if self.channel_names == ("channel1", "…"):
            assert isinstance(self.size, int)
            object.__setattr__(self, "channel_names", (f"channel{i}" for i in range(1, self.size + 1)))

        return super().model_post_init(__context)


class IndexTimeSpaceAxisBase(AxisBase):
    size: Union[Annotated[int, Gt(0)], ParametrizedSize, SizeReference, TensorAxisId] = Field(
        examples=[
            10,
            "other_axis",
            ParametrizedSize(min=32, step=16, step_with="other_tensor.axis").model_dump(),
            SizeReference(reference="other_tensor.axis").model_dump(),
            SizeReference(reference="other_axis", offset=8).model_dump(),
        ]
    )
    """The size/length of an axis can be specified as
    - fixed integer
    - parametrized series of valid sizes (`ParametrizedSize`)
    - axis reference '[tensor_name.]axis_name'
    - axis reference with optional offset (`SizeReference`)
    """


class IndexAxis(IndexTimeSpaceAxisBase):
    type: Literal["index"] = "index"
    name: ShortId = "index"


class TimeAxis(IndexTimeSpaceAxisBase):
    type: Literal["time"] = "time"
    name: ShortId = "time"
    unit: Optional[TimeUnit] = None
    scale: Annotated[float, Gt(0)] = 1.0

    @field_validator("scale")
    @classmethod
    def check_scale(cls, value: float, info: FieldValidationInfo):
        if info.data["unit"] is None and value != 1.0:
            raise ValueError("Without `unit`, `scale` may not be set.")
        return value


class SpaceAxis(IndexTimeSpaceAxisBase):
    type: Literal["space"] = "space"
    name: ShortId = Field("x", examples=["x", "y", "z"])
    unit: Optional[SpaceUnit] = None
    scale: Annotated[float, Gt(0)] = 1.0

    @field_validator("scale")
    @classmethod
    def check_scale(cls, value: float, info: FieldValidationInfo):
        if info.data["unit"] is None and value != 1.0:
            raise ValueError("Without `unit`, `scale` may not be set.")
        return value


Axis = Annotated[Union[BatchAxis, ChannelAxis, IndexAxis, TimeAxis, SpaceAxis], Field(discriminator="type")]


class OutputTimeAxis(TimeAxis, WithHalo):
    pass


class OutputSpaceAxis(SpaceAxis, WithHalo):
    pass


OutputAxis = Annotated[
    Union[BatchAxis, ChannelAxis, IndexAxis, OutputTimeAxis, OutputSpaceAxis], Field(discriminator="type")
]


TVs = Union[
    NonEmpty[Tuple[int, ...]], NonEmpty[Tuple[float, ...]], NonEmpty[Tuple[bool, ...]], NonEmpty[Tuple[str, ...]]
]


# class NominalTensor(Node):
#     level: Literal["nominal"] = "nominal"
#     values: TVs
#     """nominal values in arbitrary order"""


# class OrdinalTensor(Node):
#     level: Literal["ordinal"] = "ordinal"
#     values: TVs
#     """ordinal values in ascending order"""


class NominalOrOrdinalData(Node):
    values: TVs
    """A fixed set of nominal or an ascending sequence of ordinal values.
    String `values` are interpreted as labels for tensor values 0, ..., N.
    In this case `data_type` is required to be an unsigend integer type, e.g. 'uint8'"""
    type: Literal[
        "float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64", "bool"
    ] = Field(
        "uint8",
        examples=[
            "float32",
            "uint8",
            "uint16",
            "int64",
            "bool",
        ],
    )

    @field_validator("type")
    @classmethod
    def validate_type_matches_values(
        cls,
        typ: Literal[
            "float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64", "bool"
        ],
        info: FieldValidationInfo,
    ):
        incompatible: List[Any] = []
        for v in info.data.get("values", ()):
            if (
                (isinstance(v, (int, float)) and (v < DTYPE_LIMITS[typ].min or v > DTYPE_LIMITS[typ].max))
                or (isinstance(v, bool) and typ != "bool")
                or (isinstance(v, str) and "uint" not in typ)
            ):
                incompatible.append(v)

            if len(incompatible) == 5:
                incompatible.append("...")
                break

        if incompatible:
            raise ValueError(f"data type '{typ}' incompatible with values {incompatible}")

        return typ

    unit: Optional[Unit] = None

    @property
    def range(self):
        if isinstance(self.values[0], str):
            return 0, len(self.values) - 1
        else:
            return min(self.values), max(self.values)


class IntervalOrRatioData(Node):
    type: Literal[
        "float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64"
    ] = Field(
        "float32",
        examples=["float32", "float64", "uint8", "uint16"],
    )
    range: Tuple[Optional[float], Optional[float]] = (
        None,
        None,
    )
    """Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
    `None` corresponds to min/max of what can be expressed by `data_type`."""
    unit: Optional[Unit] = "arbitrary intensity"
    scale: float = 1.0
    """Scale for data on an interval (or ratio) scale."""
    offset: Optional[float] = None
    """Offset for data on a ratio scale."""


TensorData = Union[NominalOrOrdinalData, IntervalOrRatioData]


class ScaleLinearKwargs(v0_4.ProcessingKwargs):
    axes: Tuple[ShortId, ...] = Field((), examples=[("x", "y")])
    """The subset of axes to scale jointly.
    For example ('x', 'y') to scale two image axes for 2d data jointly."""

    gain: Union[float, Tuple[float, ...]] = 1.0
    """multiplicative factor"""

    offset: Union[float, Tuple[float, ...]] = 0.0
    """additive term"""

    @model_validator(mode="after")  # type: ignore
    def either_gain_or_offset(self) -> Self:
        if (self.gain == 1.0 or isinstance(self.gain, tuple) and all(g == 1.0 for g in self.gain)) and (
            self.offset == 0.0 or isinstance(self.offset, tuple) and all(off == 0.0 for off in self.offset)
        ):
            raise ValueError("Redunt linear scaling not allowd. Set `gain` != 1.0 and/or `offset` != 0.0.")

        return self


class ScaleLinear(v0_4.Processing):
    """Fixed linear scaling."""

    name: Literal["scale_linear"] = "scale_linear"
    kwargs: ScaleLinearKwargs


class ZeroMeanUnitVarianceKwargs(v0_4.ProcessingKwargs):
    mode: Literal["fixed", "per_dataset", "per_sample"] = Field("fixed", description=v0_4.MODE_DESCR)
    axes: Tuple[ShortId, ...] = Field((), examples=[("x", "y")])
    """The subset of axes to normalize jointly.
    For example ('x', 'y') to normalize the two image axes for 2d data jointly."""

    mean: Union[float, NonEmpty[Tuple[float, ...]], None] = Field(None, examples=[(1.1, 2.2, 3.3)])
    """The mean value(s) to use for `mode: fixed`.
    For example `[1.1, 2.2, 3.3]` in the case of a 3 channel image with `axes: xy`."""
    # todo: check if means match input axes (for mode 'fixed')

    std: Union[float, NonEmpty[Tuple[float, ...]], None] = Field(None, examples=[(0.1, 0.2, 0.3)])
    """The standard deviation values to use for `mode: fixed`. Analogous to mean."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`."""

    @model_validator(mode="after")  # type: ignore
    def mean_and_std_match_mode(self) -> Self:
        if self.mode == "fixed" and (self.mean is None or self.std is None):
            raise ValueError("`mean` and `std` are required for `mode: fixed`.")
        elif self.mode != "fixed" and (self.mean is not None or self.std is not None):
            raise ValueError(f"`mean` and `std` not allowed for `mode: {self.mode}`")

        return self


class ZeroMeanUnitVariance(v0_4.Processing):
    """Subtract mean and divide by variance."""

    name: Literal["zero_mean_unit_variance"] = "zero_mean_unit_variance"
    kwargs: ZeroMeanUnitVarianceKwargs


class ScaleRangeKwargs(v0_4.ProcessingKwargs):
    mode: Literal["per_dataset", "per_sample"]
    axes: Tuple[ShortId, ...] = Field((), examples=[("x", "y")])
    """The subset of axes to normalize jointly.
    For example ('x', 'y') to normalize the two image axes for 2d data jointly."""

    min_percentile: Annotated[float, Interval(ge=0, lt=100)] = 0.0
    """The lower percentile used for normalization."""

    max_percentile: Annotated[float, Interval(gt=1, le=100)] = 100.0
    """The upper percentile used for normalization
    Has to be bigger than `min_percentile`.
    The range is 1 to 100 instead of 0 to 100 to avoid mistakenly
    accepting percentiles specified in the range 0.0 to 1.0."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """Epsilon for numeric stability.
    `out = (tensor - v_lower) / (v_upper - v_lower + eps)`;
    with `v_lower,v_upper` values at the respective percentiles."""

    reference_tensor: Optional[Identifier] = None
    """Tensor name to compute the percentiles from. Default: The tensor itself.
    For any tensor in `inputs` only input tensor references are allowed.
    For a tensor in `outputs` only input tensor refereences are allowed if `mode: per_dataset`"""

    @field_validator("max_percentile", mode="after")
    @classmethod
    def min_smaller_max(cls, value: float, info: FieldValidationInfo):
        if (min_p := info.data["min_percentile"]) >= value:
            raise ValueError(f"min_percentile {min_p} >= max_percentile {value}")

        return value


class ScaleRange(v0_4.Processing):
    """Scale with percentiles."""

    name: Literal["scale_range"] = "scale_range"
    kwargs: ScaleRangeKwargs


class ScaleMeanVarianceKwargs(v0_4.ProcessingKwargs):
    mode: Literal["per_dataset", "per_sample"]
    reference_tensor: Identifier
    """Name of tensor to match."""

    axes: Tuple[ShortId, ...] = Field((), examples=[("x", "y")])
    """The subset of axes to scale jointly.
    For example xy to normalize the two image axes for 2d data jointly.
    Default: scale all non-batch axes jointly."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """Epsilon for numeric stability:
    "`out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean."""


class ScaleMeanVariance(v0_4.Processing):
    """Scale the tensor s.t. its mean and variance match a reference tensor."""

    name: Literal["scale_mean_variance"] = "scale_mean_variance"
    kwargs: ScaleMeanVarianceKwargs


Preprocessing = Annotated[
    Union[v0_4.Binarize, v0_4.Clip, ScaleLinear, v0_4.Sigmoid, ZeroMeanUnitVariance, ScaleRange],
    Field(discriminator="name"),
]
Postprocessing = Annotated[
    Union[v0_4.Binarize, v0_4.Clip, ScaleLinear, v0_4.Sigmoid, ZeroMeanUnitVariance, ScaleRange, ScaleMeanVariance],
    Field(discriminator="name"),
]


class TensorBase(Node):
    name: Identifier
    """Tensor name. No duplicates are allowed."""

    description: Annotated[str, MaxLen(128)] = ""

    axes: Tuple[Axis, ...]

    @field_validator("axes", mode="after")
    @classmethod
    def validate_axes(cls, axes: Tuple[Axis, ...]):
        seen_types: Set[str] = set()
        duplicate_axes_types: Set[str] = set()
        for a in axes:
            if a.type in ("time", "space"):
                continue  # duplicates allowed

            (duplicate_axes_types if a.type in seen_types else seen_types).add(a.type)

        if duplicate_axes_types:
            raise ValueError(f"Duplicate axis types: {duplicate_axes_types}")

        seen_names: Set[str] = set()
        duplicate_axes_names: Set[str] = set()
        for a in axes:
            (duplicate_axes_names if a.name in seen_names else seen_names).add(a.name)

        if duplicate_axes_names:
            raise ValueError(f"Duplicate axis names: {duplicate_axes_names}")

        return axes

    test_tensor: FileSource
    """An example tensor to use for testing.
    Using the model with the test input tensors is expected to yield the test output tensors.
    Each test tensor has be a an ndarray in the
    [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
    The file extension must be '.npy'."""

    sample_tensor: Optional[FileSource] = None
    """A sample tensor to illustrate a possible input/output for the model,
    The sample files primarily serve to inform a human user about an example use case
    and are typically stored as HDF5, PNG or TIFF images."""

    data: Union[TensorData, NonEmpty[Tuple[TensorData, ...]]] = IntervalOrRatioData()
    """Description of the tensor's data values, optionally per channel.
    If specified per channel, the data `type` needs to match across channels."""

    @field_validator("data", mode="after")
    @classmethod
    def check_data_type_across_channels(cls, value: Union[TensorData, NonEmpty[Tuple[TensorData, ...]]]):
        if not isinstance(value, tuple):
            return value

        dtypes = {t.type for t in value}
        if len(dtypes) > 1:
            raise ValueError("Tensor data descriptions per channel need to agree in their data `type`.")

        return value

    @field_validator("data", mode="after")
    @classmethod
    def check_data_matches_channelaxis(
        cls, value: Union[TensorData, NonEmpty[Tuple[TensorData, ...]]], info: FieldValidationInfo
    ):
        if not isinstance(value, tuple) or "axes" not in info.data:
            return value

        for a in info.data["axes"]:
            if isinstance(a, ChannelAxis):
                size = a.size
                assert isinstance(size, int)
                break
        else:
            return value

        if len(value) != size:
            raise ValueError(
                f"Got tensor data descriptions for {len(value)} channels, but '{a.name}' axis has size {size}."
            )

        return value


class InputTensor(TensorBase):
    name: Identifier = "input"
    """Input tensor name.
    No duplicates are allowed across all inputs and outputs."""

    preprocessing: Tuple[Preprocessing, ...] = ()
    """Description of how this input should be preprocessed."""

    @model_validator(mode="after")  # type: ignore
    def validate_preprocessing_kwargs(self) -> Self:
        axes_names = [a.name for a in self.axes]
        for p in self.preprocessing:
            kwarg_axes = p.kwargs.get("axes", ())
            if any(a not in axes_names for a in kwarg_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes names")

        return self


class OutputTensor(TensorBase):
    name: Identifier = "output"
    """Output tensor name.
    No duplicates are allowed across all inputs and outputs."""

    axes: Tuple[OutputAxis, ...]

    postprocessing: Tuple[Postprocessing, ...] = ()
    """Description of how this output should be postprocessed."""

    @model_validator(mode="after")  # type: ignore
    def validate_postprocessing_kwargs(self) -> Self:
        axes_names = [a.name for a in self.axes]
        for p in self.postprocessing:
            kwarg_axes = p.kwargs.get("axes", ())
            if any(a not in axes_names for a in kwarg_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes names")

        return self


class ArchitectureFromSource(Node):
    callable: v0_4.CallableFromSourceFile = Field(examples=["my_function.py:MyNetworkClass"])
    """Callable returning a torch.nn.Module instance.
    `<relative path to file>:<identifier of implementation within the file>`."""

    sha256: Sha256 = Field(
        description="The SHA256 of the architecture source file." + SHA256_HINT,
    )
    """The SHA256 of the callable source file."""

    kwargs: Kwargs = Field(default_factory=dict)
    """key word arguments for the `callable`"""


class ArchitectureFromDependency(Node):
    callable: v0_4.CallableFromDepencency = Field(examples=["my_module.submodule.get_my_model"])
    """callable returning a torch.nn.Module instance.
    `<dependency-package>.<[dependency-module]>.<identifier>`."""

    kwargs: Kwargs = Field(default_factory=dict)
    """key word arguments for the `callable`"""


Architecture = Union[ArchitectureFromSource, ArchitectureFromDependency]


class PytorchStateDictEntry(v0_4.WeightsEntryBase):
    type: Literal["pytorch_state_dict"] = Field("pytorch_state_dict", exclude=True)
    weights_format_name: ClassVar[str] = "Pytorch State Dict"
    architecture: Architecture

    pytorch_version: Annotated[Optional[Version], warn(Version)] = None
    """Version of the PyTorch library used.
    If `depencencies` is specified it should include pytorch and the verison has to match.
    (`dependencies` overrules `pytorch_version`)"""


class Weights(Node):
    keras_hdf5: Optional[v0_4.KerasHdf5Entry] = None
    onnx: Optional[v0_4.OnnxEntry] = None
    pytorch_state_dict: Optional[PytorchStateDictEntry] = None
    tensorflow_js: Optional[v0_4.TensorflowJsEntry] = None
    tensorflow_saved_model_bundle: Optional[v0_4.TensorflowSavedModelBundleEntry] = None
    torchscript: Optional[v0_4.TorchscriptEntry] = None

    @model_validator(mode="after")  # type: ignore
    def check_one_entry(self) -> Self:
        if all(
            entry is None
            for entry in [
                self.keras_hdf5,
                self.onnx,
                self.pytorch_state_dict,
                self.tensorflow_js,
                self.tensorflow_saved_model_bundle,
                self.torchscript,
            ]
        ):
            raise ValueError("Missing weights entry")

        return self


class ModelRdf(Node):
    rdf_source: FileSource
    """URL or relative path to a model RDF"""

    sha256: Sha256
    """SHA256 checksum of the model RDF specified under `rdf_source`."""


def get_default_partial_inputs():
    return (
        InputTensor(axes=(BatchAxis(),), test_tensor=HttpUrl("https://example.com/test.npy")).model_dump(
            exclude_unset=False, exclude={"axes", "test_tensor"}
        ),
    )


class Model(
    generic.v0_3.GenericBaseNoSource
):  # todo: do not inherite from v0_4.Model, e.g. 'inputs' are not compatible
    """Specification of the fields used in a bioimage.io-compliant RDF to describe AI models with pretrained weights.
    These fields are typically stored in a YAML file which we call a model resource description file (model RDF).
    """

    model_config = ConfigDict(
        {
            **generic.v0_3.GenericBaseNoSource.model_config,
            **ConfigDict(title="bioimage.io model specification"),
        }
    )
    """pydantic model_config"""

    format_version: Literal["0.5.0"] = "0.5.0"
    """Version of the bioimage.io model description specification used.
    When creating a new model always use the latest micro/patch version described here.
    The `format_version` is important for any consumer software to understand how to parse the fields.
    """

    type: Literal["model"] = "model"
    """Specialized resource type 'model'"""

    authors: NonEmpty[Tuple[v0_4.Author, ...]]
    """The authors are the creators of the model RDF and the primary points of contact."""

    badges: ClassVar[tuple] = ()  # type: ignore
    """Badges are not allowed for model RDFs"""

    documentation: Union[FileSource, None] = Field(
        None,
        examples=[
            "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/README.md",
            "README.md",
        ],
        in_package=True,
    )
    """URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
    The documentation should include a '[#[#]]# Validation' (sub)section
    with details on how to quantitatively validate the model on unseen data."""

    inputs: NonEmpty[Tuple[InputTensor, ...]] = Field(default_factory=get_default_partial_inputs)
    """Describes the input tensors expected by this model."""

    @field_validator("inputs", mode="after")
    @classmethod
    def validate_input_axes(cls, inputs: Tuple[InputTensor, ...]) -> Tuple[InputTensor, ...]:
        input_step_with_refs = cls._get_axes_with_parametrized_size(inputs)
        input_size_refs = cls._get_axes_with_independent_size(inputs)

        for i, ipt in enumerate(inputs):
            valid_step_with_refs = [a.name for a in ipt.axes if not isinstance(a, BatchAxis)] + input_step_with_refs
            valid_independent_refs = [a.name for a in ipt.axes if not isinstance(a, BatchAxis)] + input_size_refs
            for a, ax in enumerate(ipt.axes):
                cls._validate_axis(
                    "inputs",
                    i,
                    a,
                    ax,
                    valid_step_with_refs=valid_step_with_refs,
                    valid_independent_refs=valid_independent_refs,
                )
        return inputs

    @staticmethod
    def _validate_axis(
        field_name: str,
        i: int,
        a: int,
        axis: Union[Axis, OutputAxis],
        valid_step_with_refs: Sequence[TensorAxisId],
        valid_independent_refs: Sequence[TensorAxisId],
    ):
        if isinstance(axis, BatchAxis) or isinstance(axis.size, int):
            return

        if isinstance(axis.size, ParametrizedSize) and axis.size.step_with is not None:
            if axis.size.step_with not in valid_step_with_refs:
                raise ValueError(
                    f"Invalid tensor axis reference in {field_name}[{i}].axes[{a}].size.step_with: "
                    f"{axis.size.step_with}. Another axis's name with a parametrized size is required."
                )
            elif axis.size.step_with.split(".")[-1] == axis.name:
                raise ValueError(
                    f"Self-referencing not allowed for {field_name}[{i}].axes[{a}].size.step_with: "
                    f"{axis.size.step_with}"
                )
        elif isinstance(axis.size, SizeReference):
            if axis.size.reference not in valid_independent_refs:
                raise ValueError(
                    f"Invalid tensor axis reference at {field_name}[{i}].axes[{a}].size.reference: "
                    f"{axis.size.reference}."
                )
            elif axis.size.reference.split(".")[-1] == axis.name:
                raise ValueError(
                    f"Self-referencing not allowed for {field_name}[{i}].axes[{a}].size.reference: "
                    f"{axis.size.reference}"
                )
        elif isinstance(axis.size, str):
            if axis.size not in valid_independent_refs:
                raise ValueError(f"Invalid tensor axis reference at {field_name}[{i}].axes[{a}].size: {axis.size}.")
            elif axis.size.split(".")[-1] == axis.name:
                raise ValueError(f"Self-referencing not allowed for {field_name}[{i}].axes[{a}].size: {axis.size}.")

    license: LicenseId = Field(examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"])
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do notsupport custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
    to discuss your intentions with the community."""

    name: Annotated[
        CapitalStr,
        warn(MaxLen(64)),
    ] = Field(pattern=r"\w+[\w\- ]*\w")
    """A human-readable name of this model.
    It should be no longer than 64 characters
    and may only contain letter, number, underscore, minus or space characters."""

    outputs: NonEmpty[Tuple[OutputTensor, ...]] = Field()
    """Describes the output tensors."""

    @field_validator("outputs", mode="after")
    @classmethod
    def validate_tensor_names(
        cls, outputs: Tuple[OutputTensor, ...], info: FieldValidationInfo
    ) -> Tuple[OutputTensor, ...]:
        tensor_names = [t.name for t in info.data.get("inputs", ()) + info.data.get("outputs", ())]
        duplicate_tensor_names: List[str] = []
        seen: Set[str] = set()
        for t in tensor_names:
            if t in seen:
                duplicate_tensor_names.append(t)

            seen.add(t)

        if duplicate_tensor_names:
            raise ValueError(f"Duplicate tensor names: {duplicate_tensor_names}")

        return outputs

    @staticmethod
    def _get_axes_with_parametrized_size(io: Union[Tuple[InputTensor, ...], Tuple[OutputTensor, ...]]):
        return [
            f"{t.name}.{a.name}"
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis) and isinstance(a.size, ParametrizedSize)
        ]

    @staticmethod
    def _get_axes_with_independent_size(io: Union[Tuple[InputTensor, ...], Tuple[OutputTensor, ...]]):
        return [
            f"{t.name}.{a.name}"
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis) and (isinstance(a.size, int) or isinstance(a.size, ParametrizedSize))
        ]

    @field_validator("outputs", mode="after")
    @classmethod
    def validate_output_axes(
        cls, outputs: Tuple[OutputTensor, ...], info: FieldValidationInfo
    ) -> Tuple[OutputTensor, ...]:
        input_step_with_refs = cls._get_axes_with_parametrized_size(info.data.get("inputs", ()))
        output_step_with_refs = cls._get_axes_with_parametrized_size(outputs)

        input_size_refs = cls._get_axes_with_independent_size(info.data.get("inputs", ()))
        output_size_refs = cls._get_axes_with_independent_size(outputs)

        for i, out in enumerate(outputs):
            valid_step_with_refs = (
                [a.name for a in out.axes if not isinstance(a, BatchAxis)]
                + input_step_with_refs
                + output_step_with_refs
            )
            valid_independent_refs = (
                [a.name for a in out.axes if not isinstance(a, BatchAxis)] + input_size_refs + output_size_refs
            )
            for a, ax in enumerate(out.axes):
                cls._validate_axis(
                    "outputs",
                    i,
                    a,
                    ax,
                    valid_step_with_refs=valid_step_with_refs,
                    valid_independent_refs=valid_independent_refs,
                )

        return outputs

    packaged_by: Tuple[v0_4.Author, ...] = ()
    """The persons that have packaged and uploaded this model.
    Only required if those persons differ from the `authors`."""

    parent: Optional[Union[v0_4.LinkedModel, ModelRdf]] = None
    """The model from which this model is derived, e.g. by fine-tuning the weights."""

    run_mode: Annotated[Optional[v0_4.RunMode], warn(None)] = None
    """Custom run mode for this model: for more complex prediction procedures like test time
    data augmentation that currently cannot be expressed in the specification.
    No standard run modes are defined yet."""

    timestamp: Datetime = Field()
    """Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
    with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."""

    training_data: Union[LinkedDataset, Dataset, None] = None
    """The dataset used to train this model"""

    weights: Weights = Field()
    """The weights for this model.
    Weights can be given for different formats, but should otherwise be equivalent.
    The available weight formats determine which consumers can use this model."""

    @field_validator("weights", mode="before")
    @classmethod
    def weights_type_from_key(
        cls, data: Union[Any, Mapping[Union[Any, str], Union[Any, Mapping[Union[Any, str], Any]]]]
    ) -> Union[Any, Dict[Union[Any, str], Dict[str, Any]]]:
        if not isinstance(data, collections.abc.Mapping):
            return data

        ret: Dict[Union[Any, str], Dict[str, Any]] = dict()
        for key, value in data.items():
            ret[key] = dict(value)
            if isinstance(key, str) and isinstance(value, collections.abc.Mapping):
                if "type" in value:
                    raise ValueError(f"`type` should not be specified (redundantly) in weights entry {key}.")

                ret[key]["type"] = key  # set type to descriminate weights entry union

        return ret

    @classmethod
    def convert_from_older_format(cls, data: RawDict) -> None:
        fv = data.get("format_version")
        if not isinstance(fv, str) or fv.count(".") != 2:
            return

        major, minor = map(int, fv.split(".")[:2])
        if (major, minor) > (0, 5):
            return

        if minor == 4:
            cls.convert_model_from_v0_4_to_0_5_0(data)

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
            if isinstance(test_tensors, collections.abc.Sequence) and len(test_tensors) == len(tensor_specs):
                param["test_tensor"] = test_tensors[i]

            if isinstance(sample_tensors, collections.abc.Sequence) and len(sample_tensors) == len(tensor_specs):
                param["sample_tensor"] = sample_tensors[i]

    @classmethod
    def convert_model_from_v0_4_to_0_5_0(cls, data: RawDict) -> None:
        cls._convert_axes_string_to_axis_descriptions(data)
        cls._convert_architecture(data)
        cls._convert_attachments(data)
        _ = data.pop("download_url", None)

        data["format_version"] = "0.5.0"

    @classmethod
    def _convert_axes_string_to_axis_descriptions(cls, data: RawDict):
        inputs = data.get("inputs")
        outputs = data.get("outputs")
        sample_inputs = data.get("sample_inputs")
        sample_outputs = data.get("sample_outputs")
        test_inputs = data.pop("test_inputs", None)
        test_outputs = data.pop("test_outputs", None)

        if isinstance(inputs, collections.abc.Sequence):
            data["inputs"] = list(inputs)
            cls._update_tensor_specs(data["inputs"], test_inputs, sample_inputs)

        if isinstance(outputs, collections.abc.Sequence):
            data["outputs"] = list(outputs)
            cls._update_tensor_specs(data["outputs"], test_outputs, sample_outputs)

    @classmethod
    def _update_tensor_specs(cls, tensor_data: List[RawValue], test_tensors: Any, sample_tensors: Any):
        tts: Sequence[Any] = test_tensors if isinstance(test_tensors, collections.abc.Sequence) else ()
        sts: Sequence[Any] = sample_tensors if isinstance(sample_tensors, collections.abc.Sequence) else ()

        for idx in range(len(tensor_data)):
            d = tensor_data[idx]
            if not isinstance(d, dict):
                continue

            reordered_shape = cls._reorder_tensor_shape(d.get("shape"))
            new_d = {}
            for keep in ("name", "description"):
                if keep in d:
                    new_d[keep] = d[keep]

            if len(tts) > idx:
                new_d["test_tensor"] = tts[idx]

            if len(sts) > idx:
                new_d["sample_tensor"] = sts[idx]

            new_d["data"] = IntervalOrRatioData()

            if isinstance(d["axes"], str):
                new_axes = [
                    cls._get_axis_description_from_letter(a, reordered_shape.get(i)) for i, a in enumerate(d["axes"])
                ]
                new_d["axes"] = new_axes

            for proc in ("preprocessing", "postprocessing"):
                if (
                    isinstance(p := d.get(proc), dict)
                    and isinstance(p_kwargs := p.get("kwargs"), dict)
                    and isinstance(p_kwargs_axes := p_kwargs.get("axes"), str)
                ):
                    p_axes = [cls._get_axis_description_from_letter(a) for a in p_kwargs_axes]
                    p_kwargs["axes"] = [a.get("name", a["type"]) for a in p_axes]

            tensor_data[idx] = new_d

    @staticmethod
    def _reorder_tensor_shape(orig_shape: Union[Any, Sequence[Any], Mapping[Any, Any]]) -> Dict[int, Any]:
        if isinstance(orig_shape, collections.abc.Mapping):
            if "reference_tensor" in orig_shape:
                raise NotImplementedError(
                    "Converting tensor shapes with references from model RDF 0.4 to model RDF 0.5 is not implemented."
                )

            m: Sequence[Any] = _m if isinstance(_m := orig_shape.get("min"), collections.abc.Sequence) else []
            s: Sequence[Any] = _s if isinstance(_s := orig_shape.get("step"), collections.abc.Sequence) else []
            return {i: {"min": mm, "step": ss} for i, (mm, ss) in enumerate(zip(m, s))}
        elif isinstance(orig_shape, collections.abc.Sequence):
            return {i: s for i, s in enumerate(orig_shape)}

        return {}

    @staticmethod
    def _get_axis_description_from_letter(letter: str, size: Optional[int] = None):
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

        if size is not None and axis["type"] != "batch":
            axis["size"] = size

        return axis

    @staticmethod
    def _convert_architecture(data: Dict[str, Any]) -> None:
        weights: "Any | Dict[str, Any]" = data.get("weights")
        if not isinstance(weights, dict):
            return

        state_dict_entry: "Any | Dict[str, Any]" = weights.get("pytorch_state_dict")
        if not isinstance(state_dict_entry, dict):
            return

        callable_ = state_dict_entry.pop("architecture")
        sha = state_dict_entry.pop("architecture_sha256")
        state_dict_entry["architecture"] = dict(callable=callable_, sha256=sha)
        kwargs = state_dict_entry.pop("kwargs")
        if kwargs:
            state_dict_entry["architecture"]["kwargs"] = kwargs


AnyModel = Annotated[Union[v0_4.Model, Model], Field(discriminator="format_version")]
