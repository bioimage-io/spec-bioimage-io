import warnings
from typing import Any, ClassVar, Dict, FrozenSet, List, Literal, NewType, Optional, Set, Tuple, Union

from annotated_types import Ge, Gt, Interval, MaxLen, MinLen, Predicate
from pydantic import (
    Field,
    FieldValidationInfo,
    StringConstraints,
    TypeAdapter,
    ValidationInfo,
    field_validator,
    model_validator,  # type: ignore
)
from pydantic import HttpUrl as HttpUrl
from typing_extensions import Annotated, LiteralString, Self

from bioimageio.spec._internal.base_nodes import Kwargs, Node, NodeWithExplicitlySetFields, StringNode
from bioimageio.spec._internal.constants import DTYPE_LIMITS, INFO, SHA256_HINT
from bioimageio.spec._internal.field_warning import issue_warning, warn
from bioimageio.spec._internal.types import Datetime as Datetime
from bioimageio.spec._internal.types import DeprecatedLicenseId as DeprecatedLicenseId
from bioimageio.spec._internal.types import FileSource as FileSource
from bioimageio.spec._internal.types import Identifier as Identifier
from bioimageio.spec._internal.types import IdentifierStr, LowerCaseIdentifierStr
from bioimageio.spec._internal.types import LicenseId as LicenseId
from bioimageio.spec._internal.types import NotEmpty as NotEmpty
from bioimageio.spec._internal.types import RdfContent as RdfContent
from bioimageio.spec._internal.types import RelativeFilePath as RelativeFilePath
from bioimageio.spec._internal.types import Sha256 as Sha256
from bioimageio.spec._internal.types import Unit as Unit
from bioimageio.spec._internal.types import Version as Version
from bioimageio.spec._internal.types.field_validation import AfterValidator
from bioimageio.spec._internal.validation_context import InternalValidationContext
from bioimageio.spec.dataset.v0_3 import Dataset as Dataset
from bioimageio.spec.dataset.v0_3 import LinkedDataset as LinkedDataset
from bioimageio.spec.generic.v0_3 import Attachment as Attachment
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import Badge as Badge
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import ConfigNode as ConfigNode
from bioimageio.spec.generic.v0_3 import GenericBaseNoSource
from bioimageio.spec.generic.v0_3 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.model.v0_4 import BinarizeKwargs as BinarizeKwargs
from bioimageio.spec.model.v0_4 import CallableFromDepencency as CallableFromDepencency
from bioimageio.spec.model.v0_4 import ClipKwargs as ClipKwargs
from bioimageio.spec.model.v0_4 import KnownRunMode as KnownRunMode
from bioimageio.spec.model.v0_4 import LinkedModel as LinkedModel
from bioimageio.spec.model.v0_4 import ProcessingKwargs as ProcessingKwargs
from bioimageio.spec.model.v0_4 import RunMode as RunMode
from bioimageio.spec.model.v0_4 import WeightsEntryBase as WeightsEntryBase
from bioimageio.spec.model.v0_4 import WeightsFormat as WeightsFormat
from bioimageio.spec.model.v0_5_converter import convert_from_older_format

# unit names from https://ngff.openmicroscopy.org/latest/#axes-md
SpaceUnit = Literal[
    "attometer",
    "angstrom",
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
TensorId = NewType("TensorId", LowerCaseIdentifierStr)
_AxisId = Annotated[LowerCaseIdentifierStr, MaxLen(16)]
AxisId = NewType("AxisId", _AxisId)


def validate_tensor_axis_id(s: str):
    if s.count(".") != 1:
        raise ValueError("Expected exactly 1 dot in tensor axis id '{s}'")

    tid, an = s.split(".")
    _ = TypeAdapter(TensorId).validate_python(tid)
    _ = TypeAdapter(AxisId).validate_python(an)

    return s


TensorAxisId = Annotated[
    str, StringConstraints(min_length=1, max_length=33, pattern=r"^.+\..+$"), AfterValidator(validate_tensor_axis_id)
]
"""tensor_id.axis_id to identify a tensor axis across multiple tensors."""

NonBatchAxisId = NewType("NonBatchAxisId", Annotated[_AxisId, Predicate(lambda x: x != "batch")])

PostprocessingId = Literal[
    "binarize",
    "clip",
    "ensure_dtype",
    "fixed_zero_mean_unit_variance",
    "scale_linear",
    "scale_mean_variance",
    "scale_range",
    "sigmoid",
    "zero_mean_unit_variance",
]
PreprocessingId = Literal[
    "binarize", "clip", "ensure_dtype", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range"
]


SAME_AS_TYPE = "<same as type>"


class ParametrizedSize(Node, frozen=True):
    """Describes a range of valid tensor axis sizes as `size = min + n*step."""

    min: Annotated[int, Gt(0)]
    step: Annotated[int, Gt(0)]
    step_with: Optional[Union[AxisId, TensorAxisId]] = None
    """ID of another axis with parametrixed size to resize jointly,
    i.e. `n=n_other` for `size = min + n*step`, `size_other = min_other + n_other*step_other`.
    To step with an axis of another tensor, use `step_with = <tensor id>.<axis id>`.
    """


class SizeReference(Node, frozen=True):
    """A tensor axis size defined in relation to another reference tensor axis.

    `size = reference.size / reference.scale * axis.scale + offset`

    note:
    1. The axis and the referenced axis need to have the same unit (or no unit).
    2. A channel axis may only reference another channel axis. Their scales are implicitly set to 1.
    """

    reference: Union[AxisId, TensorAxisId]
    offset: int = 0


# this Axis definition is compatible with the NGFF draft from July 10, 2023
# https://ngff.openmicroscopy.org/latest/#axes-md
class AxisBase(NodeWithExplicitlySetFields, frozen=True):
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset({"type"})
    type: AxisType

    id: AxisId
    """An axis id unique across all axes of one tensor."""

    description: Annotated[str, MaxLen(128)] = ""

    __hash__ = NodeWithExplicitlySetFields.__hash__


class WithHalo(Node, frozen=True):
    halo: Annotated[int, Ge(0)] = 0
    """The halo should be cropped from the output tensor to avoid boundary effects.
    It is to be cropped from both sides, i.e. `size_after_crop = size - 2 * halo`.
    To document a halo that is already cropped by the model use `size.offset` instead."""


class BatchAxis(AxisBase, frozen=True):
    type: Literal["batch"] = "batch"
    id: Annotated[AxisId, Predicate(lambda x: x == AxisId("batch"))] = AxisId("batch")
    size: Optional[Literal[1]] = None
    """The batch size may be fixed to 1,
    otherwise (the default) it may be chosen arbitrarily depending on available memory"""


CHANNEL_NAMES_PLACEHOLDER = ("channel1", "channel2", "etc")
ChannelName = Annotated[IdentifierStr, StringConstraints(min_length=3, max_length=16, pattern=r"^.*\{i\}.*$")]


class ChannelAxis(AxisBase, frozen=True):
    type: Literal["channel"] = "channel"
    id: AxisId = AxisId("channel")
    channel_names: Union[Tuple[ChannelName, ...], ChannelName] = "channel{i}"
    size: Union[Annotated[int, Gt(0)], SizeReference, Literal["#channel_names"]] = "#channel_names"

    def model_post_init(self, __context: Any):
        self.model_config["frozen"] = False
        if self.size == "#channel_names":
            self.size = len(self.channel_names)  # type: ignore
            self.__pydantic_fields_set__.remove("size")

        if self.channel_names == CHANNEL_NAMES_PLACEHOLDER:
            assert isinstance(self.size, int)
            self.channel_names = tuple(f"channel{i}" for i in range(1, self.size + 1))  # type: ignore
            self.__pydantic_fields_set__.remove("channel_names")

        self.model_config["frozen"] = True
        return super().model_post_init(__context)

    @model_validator(mode="after")
    def validate_size_is_known(self):
        if self.size == "#channel_names":
            raise ValueError("Channel dimension has unknown size. Please specify `size` or `channel_names`.")

        return self


class IndexTimeSpaceAxisBase(AxisBase, frozen=True):
    size: Annotated[
        Union[Annotated[int, Gt(0)], ParametrizedSize, SizeReference, AxisId, TensorAxisId],
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
    - axis reference '[tensor_id.]axis_id'
    - axis reference with optional offset (`SizeReference`)
    """


class IndexAxis(IndexTimeSpaceAxisBase, frozen=True):
    type: Literal["index"] = "index"
    id: AxisId = AxisId("index")


class TimeAxisBase(IndexTimeSpaceAxisBase, frozen=True):
    type: Literal["time"] = "time"
    id: AxisId = AxisId("time")
    unit: Optional[TimeUnit] = None
    scale: Annotated[float, Gt(0)] = 1.0


class TimeInputAxis(TimeAxisBase, frozen=True):
    pass


class SpaceAxisBase(IndexTimeSpaceAxisBase, frozen=True):
    type: Literal["space"] = "space"
    id: Annotated[AxisId, Field(examples=["x", "y", "z"])] = AxisId("x")
    unit: Optional[SpaceUnit] = None
    scale: Annotated[float, Gt(0)] = 1.0


class SpaceInputAxis(SpaceAxisBase, frozen=True):
    pass


InputAxis = Annotated[
    Union[BatchAxis, ChannelAxis, IndexAxis, TimeInputAxis, SpaceInputAxis], Field(discriminator="type")
]


class TimeOutputAxis(TimeAxisBase, WithHalo, frozen=True):
    pass


class SpaceOutputAxis(SpaceAxisBase, WithHalo, frozen=True):
    pass


OutputAxis = Annotated[
    Union[BatchAxis, ChannelAxis, IndexAxis, TimeOutputAxis, SpaceOutputAxis], Field(discriminator="type")
]

AnyAxis = Union[InputAxis, OutputAxis]

TVs = Union[
    NotEmpty[Tuple[int, ...]], NotEmpty[Tuple[float, ...]], NotEmpty[Tuple[bool, ...]], NotEmpty[Tuple[str, ...]]
]


NominalOrOrdinalDType = Literal[
    "float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64", "bool"
]


class NominalOrOrdinalData(Node, frozen=True):
    values: TVs
    """A fixed set of nominal or an ascending sequence of ordinal values.
    String `values` are interpreted as labels for tensor values 0, ..., N.
    In this case `data_type` is required to be an unsigend integer type, e.g. 'uint8'"""

    type: Annotated[
        NominalOrOrdinalDType,
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


IntervalOrRatioDType = Literal[
    "float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64"
]


class IntervalOrRatioData(Node, frozen=True):
    type: Annotated[  # todo: rename to dtype
        IntervalOrRatioDType,
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
    unit: Optional[Unit] = "arbitrary unit"
    scale: float = 1.0
    """Scale for data on an interval (or ratio) scale."""
    offset: Optional[float] = None
    """Offset for data on a ratio scale."""


TensorData = Union[NominalOrOrdinalData, IntervalOrRatioData]


class ProcessingBase(NodeWithExplicitlySetFields, frozen=True):
    """processing base class"""

    id: Literal[PreprocessingId, PostprocessingId]
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset({"id"})


class Binarize(ProcessingBase, frozen=True):
    """Binarize the tensor with a fixed threshold.
    Values above the threshold will be set to one, values below the threshold to zero."""

    id: Literal["binarize"] = "binarize"
    kwargs: BinarizeKwargs


class Clip(ProcessingBase, frozen=True):
    """Set tensor values below min to min and above max to max."""

    id: Literal["clip"] = "clip"
    kwargs: ClipKwargs


class EnsureDtypeKwargs(ProcessingKwargs, frozen=True):
    dtype: str


class EnsureDtype(ProcessingBase, frozen=True):
    id: Literal["ensure_dtype"] = "ensure_dtype"
    kwargs: EnsureDtypeKwargs


class ScaleLinearKwargs(ProcessingKwargs, frozen=True):
    axis: Annotated[Optional[NonBatchAxisId], Field(examples=["channel"])] = None  # todo: validate existence of axis
    """The axis of non-scalar gains/offsets.
    Invalid for scalar gains/offsets.
    """

    gain: Union[float, NotEmpty[Tuple[float, ...]]] = 1.0
    """multiplicative factor"""

    offset: Union[float, NotEmpty[Tuple[float, ...]]] = 0.0
    """additive term"""

    @model_validator(mode="after")
    def either_gain_or_offset(self) -> Self:
        if (self.gain == 1.0 or isinstance(self.gain, tuple) and all(g == 1.0 for g in self.gain)) and (
            self.offset == 0.0 or isinstance(self.offset, tuple) and all(off == 0.0 for off in self.offset)
        ):
            raise ValueError("Redundant linear scaling not allowd. Set `gain` != 1.0 and/or `offset` != 0.0.")

        return self


class ScaleLinear(ProcessingBase, frozen=True):
    """Fixed linear scaling."""

    id: Literal["scale_linear"] = "scale_linear"
    kwargs: ScaleLinearKwargs


class Sigmoid(ProcessingBase, frozen=True):
    """The logistic sigmoid funciton, a.k.a. expit function."""

    id: Literal["sigmoid"] = "sigmoid"

    @property
    def kwargs(self) -> ProcessingKwargs:
        """empty kwargs"""
        return ProcessingKwargs()


class FixedZeroMeanUnitVarianceKwargs(ProcessingKwargs, frozen=True):
    """Normalize with fixed, precomputed values for mean and variance.
    See `ZeroMeanUnitVariance`/`ZeroMeanUnitVarianceKwargs` for data dependent normalization."""

    mean: Annotated[Union[float, NotEmpty[Tuple[float, ...]]], Field(examples=[3.14, (1.1, -2.2, 3.3)])]
    """The mean value(s) to normalize with. Specify `axis` for a sequence of `mean` values"""
    # todo: check if means match input axes (for mode 'fixed')

    std: Annotated[
        Union[Annotated[float, Ge(1e-6)], NotEmpty[Tuple[Annotated[float, Ge(1e-6)], ...]]],
        Field(examples=[1.05, (0.1, 0.2, 0.3)]),
    ]
    """The standard deviation value(s) to normalize with. Size must match `mean` values."""

    axis: Annotated[
        Optional[NonBatchAxisId], Field(examples=["channel", "index"])
    ] = None  # todo: validate existence of axis
    """The axis of the mean/std values to normalize each entry along that dimension separately.
    Invalid for scalar gains/offsets.
    """

    @model_validator(mode="after")
    def mean_and_std_match(self) -> Self:
        mean_len = 1 if isinstance(self.mean, (float, int)) else len(self.mean)
        std_len = 1 if isinstance(self.std, (float, int)) else len(self.std)
        if mean_len != std_len:
            raise ValueError("size of `mean` ({mean_len}) and `std` ({std_len}) must match.")

        return self


class FixedZeroMeanUnitVariance(ProcessingBase, frozen=True):
    """Subtract a given mean and divide by a given variance."""

    id: Literal["fixed_zero_mean_unit_variance"] = "fixed_zero_mean_unit_variance"
    kwargs: FixedZeroMeanUnitVarianceKwargs


class ZeroMeanUnitVarianceKwargs(ProcessingKwargs, frozen=True):
    mode: Literal["per_dataset", "per_sample"] = "per_dataset"
    """Compute percentiles independently ('per_sample') or across many samples ('per_dataset')."""

    axes: Annotated[Optional[Tuple[NonBatchAxisId, ...]], Field(examples=[("x", "y")])] = None
    """The subset of non-batch axes to normalize jointly, i.e. axes to reduce to compute mean/std.
    For example to normalize 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('x', 'y')`.
    The batch axis cannot be normalized across; use `mode=per_dataset` to normalize samples jointly
    or `mode=per_sample` to normalize samples independently.
    Default: Scale all non-batch axes jointly."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`."""


class ZeroMeanUnitVariance(ProcessingBase, frozen=True):
    """Subtract mean and divide by variance."""

    id: Literal["zero_mean_unit_variance"] = "zero_mean_unit_variance"
    kwargs: ZeroMeanUnitVarianceKwargs


class ScaleRangeKwargs(ProcessingKwargs, frozen=True):
    mode: Literal["per_dataset", "per_sample"] = "per_dataset"
    """Compute percentiles independently ('per_sample') or across many samples ('per_dataset')."""

    axes: Annotated[Optional[Tuple[NonBatchAxisId, ...]], Field(examples=[("x", "y")])] = None
    """The subset of non-batch axes to normalize jointly, i.e. axes to reduce to compute the min/max percentile value.
    For example to normalize 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('x', 'y')`.
    The batch axis cannot be normalized across; use `mode=per_dataset` to normalize samples jointly
    or `mode=per_sample` to normalize samples independently.
    Default: Scale all non-batch axes jointly."""

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

    reference_tensor: Optional[TensorId] = None
    """Tensor ID to compute the percentiles from. Default: The tensor itself.
    For any tensor in `inputs` only input tensor references are allowed.
    For a tensor in `outputs` only input tensor refereences are allowed if `mode: per_dataset`"""

    @field_validator("max_percentile", mode="after")
    @classmethod
    def min_smaller_max(cls, value: float, info: FieldValidationInfo) -> float:
        if (min_p := info.data["min_percentile"]) >= value:
            raise ValueError(f"min_percentile {min_p} >= max_percentile {value}")

        return value


class ScaleRange(ProcessingBase, frozen=True):
    """Scale with percentiles."""

    id: Literal["scale_range"] = "scale_range"
    kwargs: ScaleRangeKwargs


class ScaleMeanVarianceKwargs(ProcessingKwargs, frozen=True):
    """Scale a tensor's data distribution to match another tensor's mean/std.
    `out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean.`"""

    mode: Literal["per_dataset", "per_sample"] = "per_dataset"
    """Compute percentiles independently ('per_sample') or across many samples ('per_dataset')."""
    reference_tensor: TensorId
    """Name of tensor to match."""

    axes: Annotated[Optional[Tuple[NonBatchAxisId, ...]], Field(examples=[("x", "y")])] = None
    """The subset of non-batch axes to normalize jointly, i.e. axes to reduce to compute mean/std.
    For example to normalize 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('x', 'y')`.
    The batch axis cannot be normalized across; use `mode=per_dataset` to normalize samples jointly
    or `mode=per_sample` to normalize samples independently.
    Default: Scale all non-batch axes jointly."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """Epsilon for numeric stability:
    `out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean.`"""


class ScaleMeanVariance(ProcessingBase, frozen=True):
    """Scale the tensor s.t. its mean and variance match a reference tensor."""

    id: Literal["scale_mean_variance"] = "scale_mean_variance"
    kwargs: ScaleMeanVarianceKwargs


Preprocessing = Annotated[
    Union[
        Binarize, Clip, EnsureDtype, ScaleLinear, Sigmoid, FixedZeroMeanUnitVariance, ZeroMeanUnitVariance, ScaleRange
    ],
    Field(discriminator="id"),
]
Postprocessing = Annotated[
    Union[
        Binarize,
        Clip,
        EnsureDtype,
        ScaleLinear,
        Sigmoid,
        FixedZeroMeanUnitVariance,
        ZeroMeanUnitVariance,
        ScaleRange,
        ScaleMeanVariance,
    ],
    Field(discriminator="id"),
]


class TensorBase(Node, frozen=True):
    id: TensorId
    """Tensor id. No duplicates are allowed."""

    description: Annotated[str, MaxLen(128)] = ""

    axes: Tuple[AnyAxis, ...]

    @field_validator("axes", mode="after")
    @classmethod
    def validate_axes(cls, axes: Tuple[AxisBase, ...]) -> Tuple[AxisBase, ...]:
        seen_types: Set[str] = set()
        duplicate_axes_types: Set[str] = set()
        for a in axes:
            if a.type in ("time", "space"):
                continue  # duplicates allowed

            (duplicate_axes_types if a.type in seen_types else seen_types).add(a.type)

        if duplicate_axes_types:
            raise ValueError(f"Duplicate axis types: {duplicate_axes_types}")

        seen_ids: Set[str] = set()
        duplicate_axes_ids: Set[str] = set()
        for a in axes:
            (duplicate_axes_ids if a.id in seen_ids else seen_ids).add(a.id)

        if duplicate_axes_ids:
            raise ValueError(f"Duplicate axis ids: {duplicate_axes_ids}")

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

    data: Union[TensorData, NotEmpty[Tuple[TensorData, ...]]] = IntervalOrRatioData()
    """Description of the tensor's data values, optionally per channel.
    If specified per channel, the data `type` needs to match across channels."""

    @field_validator("data", mode="after")
    @classmethod
    def check_data_type_across_channels(
        cls, value: Union[TensorData, NotEmpty[Tuple[TensorData, ...]]]
    ) -> Union[TensorData, NotEmpty[Tuple[TensorData, ...]]]:
        if not isinstance(value, tuple):
            return value

        dtypes = {t.type for t in value}
        if len(dtypes) > 1:
            raise ValueError(
                f"Tensor data descriptions per channel need to agree in their data `type`, but found {dtypes}."
            )

        return value

    @field_validator("data", mode="after")
    @classmethod
    def check_data_matches_channelaxis(
        cls, value: Union[TensorData, NotEmpty[Tuple[TensorData, ...]]], info: FieldValidationInfo
    ) -> Union[TensorData, NotEmpty[Tuple[TensorData, ...]]]:
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
                f"Got tensor data descriptions for {len(value)} channels, but '{a.id}' axis has size {size}."
            )

        return value


class InputTensor(TensorBase, frozen=True):
    id: TensorId = TensorId("input")
    """Input tensor id.
    No duplicates are allowed across all inputs and outputs."""

    axes: NotEmpty[Tuple[InputAxis, ...]]

    preprocessing: Tuple[Preprocessing, ...] = ()
    """Description of how this input should be preprocessed."""

    @model_validator(mode="after")
    def validate_preprocessing_kwargs(self) -> Self:
        axes_ids = [a.id for a in self.axes]
        for p in self.preprocessing:
            kwarg_axes = p.kwargs.get("axes", ())
            if any(a not in axes_ids for a in kwarg_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes ids")

        return self


class OutputTensor(TensorBase, frozen=True):
    id: TensorId = TensorId("output")
    """Output tensor id.
    No duplicates are allowed across all inputs and outputs."""

    axes: Tuple[OutputAxis, ...]

    postprocessing: Tuple[Postprocessing, ...] = ()
    """Description of how this output should be postprocessed."""

    @model_validator(mode="after")
    def validate_postprocessing_kwargs(self) -> Self:
        axes_ids = [a.id for a in self.axes]
        for p in self.postprocessing:
            kwarg_axes = p.kwargs.get("axes", ())
            if any(a not in axes_ids for a in kwarg_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes ids")

        return self


AnyTensor = Union[InputTensor, OutputTensor]


class CallableFromFile(StringNode):
    _pattern = r"^.+:.+$"
    file: Union[HttpUrl, RelativeFilePath]
    """∈📦 Python module that implements `callable_name`"""
    callable_name: Identifier
    """The Python identifier of  """

    @classmethod
    def _get_data(cls, valid_string_data: str):
        *file_parts, callname = valid_string_data.split(":")
        return dict(file=":".join(file_parts), callable_name=callname)


class ArchitectureFromFile(Node, frozen=True):
    callable: Annotated[CallableFromFile, Field(examples=["my_function.py:MyNetworkClass"])]
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


class ArchitectureFromDependency(Node, frozen=True):
    callable: Annotated[CallableFromDepencency, Field(examples=["my_module.submodule.get_my_model"])]
    """callable returning a torch.nn.Module instance.
    `<dependency-package>.<[dependency-module]>.<identifier>`."""

    kwargs: Kwargs = Field(default_factory=dict)
    """key word arguments for the `callable`"""


Architecture = Union[ArchitectureFromFile, ArchitectureFromDependency]


class KerasHdf5Weights(WeightsEntryBase, frozen=True):
    type = "keras_hdf5"
    weights_format_name: ClassVar[str] = "Keras HDF5"
    tensorflow_version: Version  # todo: dynamic default from tf lib
    """TensorFlow version used to create these weights."""


class OnnxWeights(WeightsEntryBase, frozen=True):
    type = "onnx"
    weights_format_name: ClassVar[str] = "ONNX"
    opset_version: Annotated[int, Ge(7)]  # todo: dynamic default from onnx runtime
    """ONNX opset version"""


class PytorchStateDictWeights(WeightsEntryBase, frozen=True):
    type = "pytorch_state_dict"
    weights_format_name: ClassVar[str] = "Pytorch State Dict"
    architecture: Architecture

    pytorch_version: Version
    """Version of the PyTorch library used.
    If `depencencies` is specified it has to include pytorch and any version pinning has to be compatible."""


class TensorflowJsWeights(WeightsEntryBase, frozen=True):
    type = "tensorflow_js"
    weights_format_name: ClassVar[str] = "Tensorflow.js"
    tensorflow_version: Version
    """Version of the TensorFlow library used."""

    source: Union[HttpUrl, RelativeFilePath]
    """∈📦 The multi-file weights.
    All required files/folders should be a zip archive."""


class TensorflowSavedModelBundleWeights(WeightsEntryBase, frozen=True):
    type = "tensorflow_saved_model_bundle"
    weights_format_name: ClassVar[str] = "Tensorflow Saved Model"
    tensorflow_version: Version
    """Version of the TensorFlow library used."""

    source: Union[HttpUrl, RelativeFilePath]
    """∈📦 The multi-file weights.
    All required files/folders should be a zip archive."""


class TorchscriptWeights(WeightsEntryBase, frozen=True):
    type = "torchscript"
    weights_format_name: ClassVar[str] = "TorchScript"
    pytorch_version: Version
    """Version of the PyTorch library used."""


class Weights(Node, frozen=True):
    keras_hdf5: Optional[KerasHdf5Weights] = None
    onnx: Optional[OnnxWeights] = None
    pytorch_state_dict: Optional[PytorchStateDictWeights] = None
    tensorflow_js: Optional[TensorflowJsWeights] = None
    tensorflow_saved_model_bundle: Optional[TensorflowSavedModelBundleWeights] = None
    torchscript: Optional[TorchscriptWeights] = None

    @model_validator(mode="after")
    def check_entries(self, info: ValidationInfo) -> Self:
        entries = {wtype for wtype, entry in self if entry is not None}

        if not entries:
            raise ValueError("Missing weights entry")

        entries_wo_parent = {
            wtype for wtype, entry in self if entry is not None and hasattr(entry, "parent") and entry.parent is None
        }
        if len(entries_wo_parent) != 1:
            issue_warning(
                "Exactly one weights entry may not specify the `parent` field (got {value})."
                "That entry is considered the original set of model weights. "
                "Other weight formats are created through conversion of the orignal or already converted weights. "
                "They have to reference the weights format they were converted from as their `parent`.",
                value=len(entries_wo_parent),
                val_context=info.context,
            )

        for wtype, entry in self:
            if entry is None:
                continue

            assert hasattr(entry, "type")
            assert hasattr(entry, "parent")
            assert wtype == entry.type
            if entry.parent is not None and entry.parent not in entries:  # self reference checked for `parent` field
                raise ValueError(f"`weights.{wtype}.parent={entry.parent} not in specified weight formats: {entries}")

        return self

    def get(self, *priority_order: WeightsFormat):
        if not priority_order:
            priority_order = (
                "pytorch_state_dict",
                "onnx",
                "torchscript",
                "keras_hdf5",
                "tensorflow_saved_model_bundle",
                "tensorflow_js",
            )

        d = dict(self)
        for p in priority_order:
            if p not in d:
                warnings.warn(f"Encountered unknown weights format {p}")

            weights = d.get(p)
            if weights is not None:
                return weights

        raise ValueError(
            f"None of the preferred weights formats ({priority_order}) is available "
            f"({set(k for k, v in d.items() if v is not None)})."
        )


class ModelRdf(Node, frozen=True):
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


class Model(GenericBaseNoSource, frozen=True, title="bioimage.io model specification"):
    """Specification of the fields used in a bioimage.io-compliant RDF to describe AI models with pretrained weights.
    These fields are typically stored in a YAML file which we call a model resource description file (model RDF).
    """

    format_version: Literal["0.5.0"] = "0.5.0"
    """Version of the bioimage.io model description specification used.
    When creating a new model always use the latest micro/patch version described here.
    The `format_version` is important for any consumer software to understand how to parse the fields.
    """

    type: Literal["model"] = "model"
    """Specialized resource type 'model'"""

    authors: NotEmpty[Tuple[Author, ...]]
    """The authors are the creators of the model RDF and the primary points of contact."""

    badges: ClassVar[tuple] = ()  # type: ignore
    """Badges are not allowed for model RDFs"""

    documentation: Annotated[
        FileSource,  # todo: suffix
        Field(
            examples=[
                "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/README.md",
                "README.md",
            ],
        ),
    ]
    """∈📦 URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
    The documentation should include a '[#[#]]# Validation' (sub)section
    with details on how to quantitatively validate the model on unseen data."""

    inputs: NotEmpty[Tuple[InputTensor, ...]]
    """Describes the input tensors expected by this model."""

    @field_validator("inputs", mode="after")
    @classmethod
    def validate_input_axes(cls, inputs: Tuple[InputTensor, ...]) -> Tuple[InputTensor, ...]:
        input_step_with_refs = cls._get_axes_with_parametrized_size(inputs)
        input_size_refs = cls._get_axes_with_independent_size(inputs)

        for i, ipt in enumerate(inputs):
            valid_step_with_refs: Dict[Union[AxisId, TensorAxisId], Tuple[AnyTensor, AnyAxis, ParametrizedSize]] = {
                **{
                    a.id: (ipt, a, a.size)
                    for a in ipt.axes
                    if not isinstance(a, BatchAxis) and isinstance(a.size, ParametrizedSize)
                },
                **input_step_with_refs,
            }
            valid_independent_refs: Dict[
                Union[AxisId, TensorAxisId], Tuple[AnyTensor, AnyAxis, Union[int, ParametrizedSize]]
            ] = {
                **{
                    a.id: (ipt, a, a.size)
                    for a in ipt.axes
                    if not isinstance(a, BatchAxis) and isinstance(a.size, (int, ParametrizedSize))
                },
                **input_size_refs,
            }
            for a, ax in enumerate(ipt.axes):
                cls._validate_axis(
                    "inputs",
                    i,
                    ipt.id,
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
        tensor_id: str,
        a: int,
        axis: AnyAxis,
        valid_step_with_refs: Dict[Union[AxisId, TensorAxisId], Tuple[AnyTensor, AnyAxis, ParametrizedSize]],
        valid_independent_refs: Dict[
            Union[AxisId, TensorAxisId], Tuple[AnyTensor, AnyAxis, Union[int, ParametrizedSize]]
        ],
    ):
        if isinstance(axis, BatchAxis) or isinstance(axis.size, int):
            return

        if isinstance(axis.size, ParametrizedSize) and axis.size.step_with is not None:
            if axis.size.step_with not in valid_step_with_refs:
                raise ValueError(
                    f"Invalid tensor axis reference in {field_name}[{i}].axes[{a}].size.step_with: "
                    f"{axis.size.step_with}. Another (tensor's) axis id with a parametrized size is required."
                )
            if axis.size.step_with in (axis.id, f"{tensor_id}.{axis.id}"):
                raise ValueError(
                    f"Self-referencing not allowed for {field_name}[{i}].axes[{a}].size.step_with: "
                    f"{axis.size.step_with}"
                )
            if isinstance(axis, WithHalo) and (axis.size.min - 2 * axis.halo) < 1:
                raise ValueError(f"axis {axis.id} with minimum size {axis.size.min} is too small for halo {axis.halo}.")

        elif isinstance(axis.size, SizeReference):
            if axis.size.reference not in valid_independent_refs:
                raise ValueError(
                    f"Invalid tensor axis reference at {field_name}[{i}].axes[{a}].size.reference: "
                    f"{axis.size.reference}."
                )
            if axis.size.reference in (axis.id, f"{tensor_id}.{axis.id}"):
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
            min_size = valid_independent_refs[axis.size.reference][2]
            if isinstance(min_size, ParametrizedSize):
                min_size = min_size.min

            if isinstance(axis, WithHalo) and (min_size - 2 * axis.halo) < 1:
                raise ValueError(f"axis {axis.id} with minimum size {min_size} is too small for halo {axis.halo}.")

        elif isinstance(axis.size, str):
            if axis.size not in valid_independent_refs:
                raise ValueError(f"Invalid tensor axis reference at {field_name}[{i}].axes[{a}].size: {axis.size}.")
            if axis.size in (axis.id, f"{tensor_id}.{axis.id}"):
                raise ValueError(f"Self-referencing not allowed for {field_name}[{i}].axes[{a}].size: {axis.size}.")
            if axis.type == "channel" and valid_independent_refs[axis.size][1].type != "channel":
                raise ValueError("A channel axis' size may only reference another fixed size channel axis.")

    license: Annotated[
        Union[LicenseId, DeprecatedLicenseId],
        warn(LicenseId, "{value} is deprecated, see https://spdx.org/licenses/{value}.html"),
        Field(examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"]),
    ]
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do not support custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
    to discuss your intentions with the community."""

    name: Annotated[
        str,
        MinLen(5),
        warn(MaxLen(64), "Name longer than 64 characters.", INFO),
    ]
    """A human-readable name of this model.
    It should be no longer than 64 characters
    and may only contain letter, number, underscore, minus or space characters."""

    outputs: NotEmpty[Tuple[OutputTensor, ...]]
    """Describes the output tensors."""

    @field_validator("outputs", mode="after")
    @classmethod
    def validate_tensor_ids(
        cls, outputs: Tuple[OutputTensor, ...], info: FieldValidationInfo
    ) -> Tuple[OutputTensor, ...]:
        tensor_ids = [t.id for t in info.data.get("inputs", ()) + info.data.get("outputs", ())]
        duplicate_tensor_ids: List[str] = []
        seen: Set[str] = set()
        for t in tensor_ids:
            if t in seen:
                duplicate_tensor_ids.append(t)

            seen.add(t)

        if duplicate_tensor_ids:
            raise ValueError(f"Duplicate tensor ids: {duplicate_tensor_ids}")

        return outputs

    @staticmethod
    def _get_axes_with_parametrized_size(io: Union[Tuple[InputTensor, ...], Tuple[OutputTensor, ...]]):
        return {
            f"{t.id}.{a.id}": (t, a, a.size)
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis) and isinstance(a.size, ParametrizedSize)
        }

    @staticmethod
    def _get_axes_with_independent_size(io: Union[Tuple[InputTensor, ...], Tuple[OutputTensor, ...]]):
        return {
            f"{t.id}.{a.id}": (t, a, a.size)
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis) and isinstance(a.size, (int, ParametrizedSize))
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
            valid_step_with_refs: Dict[Union[AxisId, TensorAxisId], Tuple[AnyTensor, AnyAxis, ParametrizedSize]] = {
                **{
                    a.id: (out, a, a.size)
                    for a in out.axes
                    if not isinstance(a, BatchAxis) and isinstance(a.size, ParametrizedSize)
                },
                **input_step_with_refs,
                **output_step_with_refs,
            }
            valid_independent_refs: Dict[
                Union[AxisId, TensorAxisId], Tuple[AnyTensor, AnyAxis, Union[int, ParametrizedSize]]
            ] = {
                **{
                    a.id: (out, a, a.size)
                    for a in out.axes
                    if not isinstance(a, BatchAxis) and isinstance(a.size, (int, ParametrizedSize))
                },
                **input_size_refs,
                **output_size_refs,
            }
            for a, ax in enumerate(out.axes):
                cls._validate_axis(
                    "outputs",
                    i,
                    out.id,
                    a,
                    ax,
                    valid_step_with_refs=valid_step_with_refs,
                    valid_independent_refs=valid_independent_refs,
                )

        return outputs

    packaged_by: Tuple[Author, ...] = ()
    """The persons that have packaged and uploaded this model.
    Only required if those persons differ from the `authors`."""

    parent: Optional[Union[LinkedModel, ModelRdf]] = None
    """The model from which this model is derived, e.g. by fine-tuning the weights."""

    run_mode: Annotated[
        Optional[RunMode], warn(None, "Run mode '{value}' has limited support across consumer softwares.")
    ] = None
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

    @classmethod
    def convert_from_older_format(cls, data: RdfContent, context: InternalValidationContext) -> None:
        super().convert_from_older_format(data, context)
        convert_from_older_format(data, context)
