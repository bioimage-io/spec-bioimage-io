import collections.abc
from typing import Any, ClassVar, Dict, List, Literal, Mapping, Optional, Set, Tuple, Union

from annotated_types import Ge, Gt, Interval, MaxLen, MinLen
from pydantic import (
    ConfigDict,
    Field,
    FieldValidationInfo,
    StringConstraints,
    ValidationInfo,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated, Self

from bioimageio.spec import generic
from bioimageio.spec._internal._constants import (
    DTYPE_LIMITS,
    ERROR,
    INFO,
    SHA256_HINT,
    WARNING,
    WARNING_LEVEL_CONTEXT_KEY,
)
from bioimageio.spec._internal._validate import Predicate, ValContext
from bioimageio.spec._internal._warn import warn
from bioimageio.spec._internal.base_nodes import Kwargs, Node
from bioimageio.spec.dataset import Dataset
from bioimageio.spec.dataset.v0_3 import LinkedDataset
from bioimageio.spec.model.v0_5_converter import convert_from_older_format
from bioimageio.spec.types import (
    Datetime,
    DeprecatedLicenseId,
    FileSource,
    Identifier,
    LicenseId,
    NonEmpty,
    RawDict,
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
OtherTensorAxisId = Annotated[
    str, StringConstraints(min_length=1, max_length=33, pattern=r"^.*\..*$"), Predicate(str.islower)
]
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
    """A tensor axis size defined in relation to another reference tensor axis.

    `size = reference.size / reference.scale * axis.scale + offset`

    note:
    1. The axis and the referenced axis need to have the same unit (or no unit).
    2. A channel axis may only reference another channel axis. Their scales are implicitly set to 1.
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
    size: Optional[Literal[1]] = None
    """The batch size may be fixed to 1,
    otherwise (the default) it may be chosen arbitrarily depending on available memory"""


CHANNEL_NAMES_PLACEHOLDER = ("channel1", "channel2", "etc")
ChannelNamePattern = Annotated[str, StringConstraints(min_length=3, max_length=16, pattern=r"^.*\{i\}.*$")]


class ChannelAxis(AxisBase):
    type: Literal["channel"] = "channel"
    name: ShortId = "channel"
    channel_names: Union[Tuple[ShortId, ...], ChannelNamePattern] = "channel{i}"
    size: Union[Annotated[int, Gt(0)], SizeReference, Literal["#channel_names"]] = "#channel_names"

    def model_post_init(self, __context: Any):
        if self.size == "#channel_names":
            object.__setattr__(self, "size", len(self.channel_names))

        if self.channel_names == CHANNEL_NAMES_PLACEHOLDER:
            assert isinstance(self.size, int)
            object.__setattr__(self, "channel_names", (f"channel{i}" for i in range(1, self.size + 1)))

        return super().model_post_init(__context)


class IndexTimeSpaceAxisBase(AxisBase):
    size: Annotated[
        Union[Annotated[int, Gt(0)], ParametrizedSize, SizeReference, TensorAxisId],
        Field(
            examples=[
                10,
                "other_axis",
                ParametrizedSize(min=32, step=16, step_with="other_tensor.axis").model_dump(),
                SizeReference(reference="other_tensor.axis").model_dump(),
                SizeReference(reference="other_axis", offset=8).model_dump(),
            ]
        ),
    ]
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


class SpaceAxis(IndexTimeSpaceAxisBase):
    type: Literal["space"] = "space"
    name: Annotated[ShortId, Field(examples=["x", "y", "z"])] = "x"
    unit: Optional[SpaceUnit] = None
    scale: Annotated[float, Gt(0)] = 1.0


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


class NominalOrOrdinalData(Node):
    values: TVs
    """A fixed set of nominal or an ascending sequence of ordinal values.
    String `values` are interpreted as labels for tensor values 0, ..., N.
    In this case `data_type` is required to be an unsigend integer type, e.g. 'uint8'"""

    type: Annotated[
        Literal["float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64", "bool"],
        Field(
            examples=[
                "float32",
                "uint8",
                "uint16",
                "int64",
                "bool",
            ],
        ),
    ] = "uint8"

    @model_validator(mode="after")
    def validate_values_match_type(
        self,
    ) -> Self:
        incompatible: List[Any] = []
        for v in self.values:
            if (
                (isinstance(v, (int, float)) and (v < DTYPE_LIMITS[self.type].min or v > DTYPE_LIMITS[self.type].max))
                or (isinstance(v, bool) and self.type != "bool")
                or (isinstance(v, str) and "uint" not in self.type)
                or (isinstance(v, float) and "int" in self.type)
            ):
                incompatible.append(v)

            if len(incompatible) == 5:
                incompatible.append("...")
                break

        if incompatible:
            raise ValueError(f"data type '{self.type}' incompatible with values {incompatible}")

        return self

    unit: Optional[Unit] = None

    @property
    def range(self):
        if isinstance(self.values[0], str):
            return 0, len(self.values) - 1
        else:
            return min(self.values), max(self.values)


class IntervalOrRatioData(Node):
    type: Annotated[
        Literal["float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64"],
        Field(
            examples=["float32", "float64", "uint8", "uint16"],
        ),
    ] = "float32"
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
    axes: Annotated[Tuple[ShortId, ...], Field(examples=[("x", "y")])] = ()
    """The subset of axes to scale jointly.
    For example ('x', 'y') to scale two image axes for 2d data jointly."""

    gain: Union[float, Tuple[float, ...]] = 1.0
    """multiplicative factor"""

    offset: Union[float, Tuple[float, ...]] = 0.0
    """additive term"""

    @model_validator(mode="after")
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
    mode: Literal["fixed", "per_dataset", "per_sample"] = "fixed"
    """Mode for computing mean and variance.
    |     mode    |             description              |
    | ----------- | ------------------------------------ |
    |   fixed     | Fixed values for mean and variance   |
    | per_dataset | Compute for the entire dataset       |
    | per_sample  | Compute for each sample individually |
    """
    axes: Annotated[Tuple[ShortId, ...], Field(examples=[("x", "y")])] = ()
    """The subset of axes to normalize jointly.
    For example ('x', 'y') to normalize the two image axes for 2d data jointly."""

    mean: Annotated[Union[float, NonEmpty[Tuple[float, ...]], None], Field(examples=[(1.1, 2.2, 3.3)])] = None
    """The mean value(s) to use for `mode: fixed`.
    For example `[1.1, 2.2, 3.3]` in the case of a 3 channel image with `axes: xy`."""
    # todo: check if means match input axes (for mode 'fixed')

    std: Annotated[Union[float, NonEmpty[Tuple[float, ...]], None], Field(examples=[(0.1, 0.2, 0.3)])] = None
    """The standard deviation values to use for `mode: fixed`. Analogous to mean."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`."""

    @model_validator(mode="after")
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
    axes: Annotated[Tuple[ShortId, ...], Field(examples=[("x", "y")])] = ()
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
    def min_smaller_max(cls, value: float, info: FieldValidationInfo) -> float:
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

    axes: Annotated[Tuple[ShortId, ...], Field(examples=[("x", "y")])] = ()
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
    def validate_axes(cls, axes: Tuple[Axis, ...]) -> Tuple[Axis, ...]:
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
    def check_data_type_across_channels(
        cls, value: Union[TensorData, NonEmpty[Tuple[TensorData, ...]]]
    ) -> Union[TensorData, NonEmpty[Tuple[TensorData, ...]]]:
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
    ) -> Union[TensorData, NonEmpty[Tuple[TensorData, ...]]]:
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

    @model_validator(mode="after")
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

    @model_validator(mode="after")
    def validate_postprocessing_kwargs(self) -> Self:
        axes_names = [a.name for a in self.axes]
        for p in self.postprocessing:
            kwarg_axes = p.kwargs.get("axes", ())
            if any(a not in axes_names for a in kwarg_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes names")

        return self


class ArchitectureFromSource(Node):
    callable: Annotated[v0_4.CallableFromSourceFile, Field(examples=["my_function.py:MyNetworkClass"])]
    """Callable returning a torch.nn.Module instance.
    `<relative path to file>:<identifier of implementation within the file>`."""

    sha256: Annotated[
        Sha256,
        Field(
            description="The SHA256 of the architecture source file." + SHA256_HINT,
        ),
    ]
    """The SHA256 of the callable source file."""

    kwargs: Kwargs = Field(default_factory=dict)
    """key word arguments for the `callable`"""


class ArchitectureFromDependency(Node):
    callable: Annotated[v0_4.CallableFromDepencency, Field(examples=["my_module.submodule.get_my_model"])]
    """callable returning a torch.nn.Module instance.
    `<dependency-package>.<[dependency-module]>.<identifier>`."""

    kwargs: Kwargs = Field(default_factory=dict)
    """key word arguments for the `callable`"""


Architecture = Union[ArchitectureFromSource, ArchitectureFromDependency]


class PytorchStateDictWeights(v0_4.WeightsEntryBase):
    type: Annotated[Literal["pytorch_state_dict"], Field(exclude=True)] = "pytorch_state_dict"
    weights_format_name: ClassVar[str] = "Pytorch State Dict"
    architecture: Architecture

    pytorch_version: Annotated[Optional[Version], warn(Version)] = None
    """Version of the PyTorch library used.
    If `depencencies` is specified it should include pytorch and the verison has to match.
    (`dependencies` overrules `pytorch_version`)"""


class Weights(Node):
    keras_hdf5: Optional[v0_4.KerasHdf5Weights] = None
    onnx: Optional[v0_4.OnnxWeights] = None
    pytorch_state_dict: Optional[PytorchStateDictWeights] = None
    tensorflow_js: Optional[v0_4.TensorflowJsWeights] = None
    tensorflow_saved_model_bundle: Optional[v0_4.TensorflowSavedModelBundleWeights] = None
    torchscript: Optional[v0_4.TorchscriptWeights] = None

    @model_validator(mode="after")
    def check_entries(self, info: ValidationInfo) -> Self:
        entries = {name for name, entry in self if entry is not None}

        if not entries:
            raise ValueError("Missing weights entry")

        entries_wo_parent = {name for name, entry in self if entry is not None and entry.parent is None}

        if len(entries_wo_parent) != 1 and WARNING >= (info.context or {}).get(WARNING_LEVEL_CONTEXT_KEY, ERROR):
            raise ValueError(
                "Exactly one weights entry that does not specify the `parent` field is required. "
                "That entry is considered the original set of model weights. "
                "Other weight formats are created through conversion of the orignal or already converted weights. "
                "They have to reference the weights format they were converted from as their `parent`."
            )

        for name, entry in self:
            if entry is None:
                continue

            assert hasattr(entry, "type")
            assert hasattr(entry, "parent")
            assert name == entry.type
            if entry.parent is not None and entry.parent not in entries:  # self reference checked for `parent` field
                raise ValueError(f"`weights.{name}.parent={entry.parent} not in specified weight formats: {entries}")

        return self


class ModelRdf(Node):
    rdf_source: FileSource
    """URL or relative path to a model RDF"""

    sha256: Sha256
    """SHA256 checksum of the model RDF specified under `rdf_source`."""


# def get_default_partial_inputs():
#     return (
#         InputTensor(axes=(BatchAxis(),), test_tensor=HttpUrl("https://example.com/test.npy")).model_dump(
#             exclude_unset=False, exclude={"axes", "test_tensor"}
#         ),
#     )


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

    documentation: Annotated[
        Optional[FileSource],
        Field(
            examples=[
                "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/README.md",
                "README.md",
            ],
        ),
    ] = None
    """∈📦 URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
    The documentation should include a '[#[#]]# Validation' (sub)section
    with details on how to quantitatively validate the model on unseen data."""

    inputs: NonEmpty[Tuple[InputTensor, ...]]
    """Describes the input tensors expected by this model."""

    @field_validator("inputs", mode="after")
    @classmethod
    def validate_input_axes(cls, inputs: Tuple[InputTensor, ...]) -> Tuple[InputTensor, ...]:
        input_step_with_refs = cls._get_axes_with_parametrized_size(inputs)
        input_size_refs = cls._get_axes_with_independent_size(inputs)

        for i, ipt in enumerate(inputs):
            valid_step_with_refs = {
                **{a.name: (ipt, a) for a in ipt.axes if not isinstance(a, BatchAxis)},
                **input_step_with_refs,
            }
            valid_independent_refs = {
                **{a.name: (ipt, a) for a in ipt.axes if not isinstance(a, BatchAxis)},
                **input_size_refs,
            }
            for a, ax in enumerate(ipt.axes):
                cls._validate_axis(
                    "inputs",
                    i,
                    ipt.name,
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
        tensor_name: str,
        a: int,
        axis: Union[Axis, OutputAxis],
        valid_step_with_refs: Dict[TensorAxisId, Tuple[Union[InputTensor, OutputTensor], Axis]],
        valid_independent_refs: Dict[TensorAxisId, Tuple[Union[InputTensor, OutputTensor], Axis]],
    ):
        if isinstance(axis, BatchAxis) or isinstance(axis.size, int):
            return

        if isinstance(axis.size, ParametrizedSize) and axis.size.step_with is not None:
            if axis.size.step_with not in valid_step_with_refs:
                raise ValueError(
                    f"Invalid tensor axis reference in {field_name}[{i}].axes[{a}].size.step_with: "
                    f"{axis.size.step_with}. Another axis's name with a parametrized size is required."
                )
            if axis.size.step_with in (axis.name, f"{tensor_name}.{axis.name}"):
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
            if axis.size.reference in (axis.name, f"{tensor_name}.{axis.name}"):
                raise ValueError(
                    f"Self-referencing not allowed for {field_name}[{i}].axes[{a}].size.reference: "
                    f"{axis.size.reference}"
                )
            if axis.type == "channel" and valid_independent_refs[axis.size.reference][1].type != "channel":
                raise ValueError("A channel axis' size may only reference another fixed size channel axis.")
            if (ax_unit := getattr(axis, "unit", None)) != (
                ref_unit := getattr(valid_independent_refs[axis.size.reference][1], "unit", None)
            ):
                raise ValueError(
                    f"The units of an axis and its reference axis need to match, but '{ax_unit}' != '{ref_unit}'."
                )

        elif isinstance(axis.size, str):
            if axis.size not in valid_independent_refs:
                raise ValueError(f"Invalid tensor axis reference at {field_name}[{i}].axes[{a}].size: {axis.size}.")
            if axis.size in (axis.name, f"{tensor_name}.{axis.name}"):
                raise ValueError(f"Self-referencing not allowed for {field_name}[{i}].axes[{a}].size: {axis.size}.")
            if axis.type == "channel" and valid_independent_refs[axis.size][1].type != "channel":
                raise ValueError("A channel axis' size may only reference another fixed size channel axis.")

    license: Annotated[
        Union[LicenseId, DeprecatedLicenseId],
        warn(LicenseId, msg="{value} is deprecated, see https://spdx.org/licenses/{value}.html"),
        Field(examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"]),
    ]
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do not support custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
    to discuss your intentions with the community."""

    name: Annotated[
        str,
        MinLen(5),
        warn(MaxLen(64), INFO),
    ]
    """A human-readable name of this model.
    It should be no longer than 64 characters
    and may only contain letter, number, underscore, minus or space characters."""

    outputs: NonEmpty[Tuple[OutputTensor, ...]]
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
        return {
            f"{t.name}.{a.name}": (t, a)
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis) and isinstance(a.size, ParametrizedSize)
        }

    @staticmethod
    def _get_axes_with_independent_size(io: Union[Tuple[InputTensor, ...], Tuple[OutputTensor, ...]]):
        return {
            f"{t.name}.{a.name}": (t, a)
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis) and (isinstance(a.size, int) or isinstance(a.size, ParametrizedSize))
        }

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
            valid_step_with_refs = {
                **{a.name: (out, a) for a in out.axes if not isinstance(a, BatchAxis)},
                **input_step_with_refs,
                **output_step_with_refs,
            }
            valid_independent_refs = {
                **{a.name: (out, a) for a in out.axes if not isinstance(a, BatchAxis)},
                **input_size_refs,
                **output_size_refs,
            }
            for a, ax in enumerate(out.axes):
                cls._validate_axis(
                    "outputs",
                    i,
                    out.name,
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

    timestamp: Datetime
    """Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
    with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."""

    training_data: Union[LinkedDataset, Dataset, None] = None
    """The dataset used to train this model"""

    weights: Weights
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
    def convert_from_older_format(cls, data: RawDict, context: ValContext) -> None:
        convert_from_older_format(data, context)


AnyModel = Annotated[Union[v0_4.Model, Model], Field(discriminator="format_version")]
