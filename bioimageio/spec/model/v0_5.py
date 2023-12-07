from __future__ import annotations

import collections.abc
from abc import ABC
from datetime import datetime
from pathlib import PurePosixPath
from typing import (
    Any,
    ClassVar,
    Dict,
    FrozenSet,
    Generic,
    List,
    Literal,
    Mapping,
    NewType,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)

import numpy as np
from annotated_types import Ge, Gt, Interval, MaxLen, MinLen, Predicate
from imageio.v3 import imread  # pyright: ignore[reportUnknownVariableType]
from numpy.typing import NDArray
from pydantic import (
    Field,
    StringConstraints,
    TypeAdapter,
    ValidationInfo,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated, LiteralString, Self, assert_never

from bioimageio.spec._internal.base_nodes import Node, NodeWithExplicitlySetFields
from bioimageio.spec._internal.constants import DTYPE_LIMITS, INFO
from bioimageio.spec._internal.field_warning import issue_warning, warn
from bioimageio.spec._internal.io_utils import download, load_array
from bioimageio.spec._internal.types import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec._internal.types import BioimageioYamlContent as BioimageioYamlContent
from bioimageio.spec._internal.types import Datetime as Datetime
from bioimageio.spec._internal.types import DeprecatedLicenseId as DeprecatedLicenseId
from bioimageio.spec._internal.types import FileSource as FileSource
from bioimageio.spec._internal.types import HttpUrl as HttpUrl
from bioimageio.spec._internal.types import Identifier as Identifier
from bioimageio.spec._internal.types import LicenseId as LicenseId
from bioimageio.spec._internal.types import LowerCaseIdentifierStr, SiUnit
from bioimageio.spec._internal.types import NotEmpty as NotEmpty
from bioimageio.spec._internal.types import RelativeFilePath as RelativeFilePath
from bioimageio.spec._internal.types import ResourceId as ResourceId
from bioimageio.spec._internal.types import Sha256 as Sha256
from bioimageio.spec._internal.types import Version as Version
from bioimageio.spec._internal.types.field_validation import WithSuffix
from bioimageio.spec._internal.validation_context import InternalValidationContext, get_internal_validation_context
from bioimageio.spec.dataset.v0_3 import DatasetDescr as DatasetDescr
from bioimageio.spec.dataset.v0_3 import LinkedDatasetDescr as LinkedDatasetDescr
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import Doi as Doi
from bioimageio.spec.generic.v0_3 import FileDescr as FileDescr
from bioimageio.spec.generic.v0_3 import GenericModelDescrBase, MarkdownSource
from bioimageio.spec.generic.v0_3 import LinkedResourceDescr as LinkedResourceDescr
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.model.v0_4 import BinarizeKwargs as BinarizeKwargs
from bioimageio.spec.model.v0_4 import CallableFromDepencency as CallableFromDepencency
from bioimageio.spec.model.v0_4 import ClipKwargs as ClipKwargs
from bioimageio.spec.model.v0_4 import KnownRunMode as KnownRunMode
from bioimageio.spec.model.v0_4 import LinkedModel as LinkedModel
from bioimageio.spec.model.v0_4 import ProcessingKwargs as ProcessingKwargs
from bioimageio.spec.model.v0_4 import RunMode as RunMode
from bioimageio.spec.model.v0_4 import WeightsFormat as WeightsFormat
from bioimageio.spec.model.v0_5_converter import convert_from_older_format
from bioimageio.spec.utils import download, load_array

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
        raise ValueError(f"Expected exactly 1 dot in tensor axis id '{s}'")

    tid, an = s.split(".")
    _ = TypeAdapter(TensorId).validate_python(tid)
    _ = TypeAdapter(AxisId).validate_python(an)

    return s


class TensorAxisId(Node):
    tensor_id: TensorId
    axis_id: AxisId

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


class ParameterizedSize(Node):
    """Describes a range of valid tensor axis sizes as `size = min + n*step`.
    `n` in this equation is the same for all axis parametrized in this manner across the whole model."""

    min: Annotated[int, Gt(0)]
    step: Annotated[int, Gt(0)]

    def transformed(self, *, scale: float = 1.0, offset: int = 0) -> "ParameterizedSize":
        return ParameterizedSize(
            min=round(self.min * scale) + offset, #FIXME: does rounding make sense?
            step=round(self.step * scale) #FIXME: does rounding make sense?
        )

    def validate_size(self, size: int) -> int:
        if size < self.min:
            raise ValueError(f"size {size} < {self.min}")
        if (size - self.min) % self.step != 0:
            raise ValueError(
                f"axis of size {size} is not parametrized by `min + n*step` = `{self.min} + n*{self.step}`"
            )

        return size


class SizeReference(Node):
    """A tensor axis size defined in relation to another reference tensor axis.

    `size = reference.size / reference.scale * axis.scale + offset`

    note:
    1. The axis and the referenced axis need to have the same unit (or no unit).
    2. A channel axis may only reference another channel axis. Their scales are implicitly set to 1.
    """

    reference: TensorAxisId
    scale: Annotated[float, Gt(0)] = 1.0
    offset: int = 0

    def try_resolve(
        self,
        *,
        others: Mapping[TensorId, Mapping[AxisId, AxisSize]],
        visited: "Set[TensorId] | None" = None,
    ) -> "int | ParameterizedSize | None":
        visited = visited or set()
        if self.reference.tensor_id in visited:
            return None
        axes_sizes = others.get(self.reference.tensor_id)
        if axes_sizes is None:
            return None
        visited.add(self.reference.tensor_id)
        size = axes_sizes.get(self.reference.axis_id)
        if size is None:
            return None
        if isinstance(size, int):
            return int(size / 1 * self.scale + self.offset)
        if isinstance(size, ParameterizedSize):
            return size.transformed(scale=self.scale, offset=self.offset)
        return size.try_resolve(others=others, visited=visited)

    def validate_size(
        self,
        size: int,
        *,
        known_tensor_sizes: Mapping[TensorId, Mapping[AxisId, int]],
    ):
        tensor_id = self.reference.tensor_id
        axis_id = self.reference.axis_id

        other_tensor_sizes = known_tensor_sizes.get(tensor_id)
        if other_tensor_sizes is None:
            raise ValueError(f"tensor sizes of '{tensor_id}' are unknown.")

        other_axis_size = other_tensor_sizes.get(axis_id)
        if other_axis_size is None:
            raise ValueError(f"axis size '{axis_id}' is unknown.")

        if size != other_axis_size:
            raise ValueError(
                f"axis size mismatch: axis {tensor_id}.{axis_id} of size " f"{size} != {other_axis_size} given by {size}."
            )

AxisSize: TypeAlias = Union[int, SizeReference, ParameterizedSize]

# this Axis definition is compatible with the NGFF draft from July 10, 2023
# https://ngff.openmicroscopy.org/latest/#axes-md
class AxisBase(NodeWithExplicitlySetFields):
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset({"type"})

    id: AxisId
    """An axis id unique across all axes of one tensor."""

    @model_validator(mode="before")
    @classmethod
    def convert_name_to_id(cls, data: Dict[str, Any], info: ValidationInfo):
        context = get_internal_validation_context(info.context)
        if (
            "name" in data
            and "id" not in data
            and "original_format" in context
            and context["original_format"].release[:2] <= (0, 4)
        ):
            data["id"] = data.pop("name")

        return data

    description: Annotated[str, MaxLen(128)] = ""

    __hash__ = NodeWithExplicitlySetFields.__hash__


class WithHalo(Node):
    halo: Annotated[int, Ge(0)] = 0
    """The halo should be cropped from the output tensor to avoid boundary effects.
    It is to be cropped from both sides, i.e. `size_after_crop = size - 2 * halo`.
    To document a halo that is already cropped by the model use `size.offset` instead."""


class BatchAxis(AxisBase):
    type: Literal["batch"] = "batch"
    id: Annotated[AxisId, Predicate(lambda x: x == AxisId("batch"))] = AxisId("batch")
    size: Optional[Literal[1]] = None
    """The batch size may be fixed to 1,
    otherwise (the default) it may be chosen arbitrarily depending on available memory"""


GenericChannelName = Annotated[str, StringConstraints(min_length=3, max_length=16, pattern=r"^.*\{i\}.*$")]


class ChannelAxis(AxisBase):
    type: Literal["channel"] = "channel"
    id: AxisId = AxisId("channel")
    channel_names: Union[List[Identifier], Identifier, GenericChannelName] = "channel{i}"
    size: Union[Annotated[int, Gt(0)], SizeReference] = "#channel_names"  # type: ignore

    @model_validator(mode="before")
    @classmethod
    def set_size_or_channel_names(cls, data: Dict[str, Any]):
        channel_names: Union[Any, Sequence[Any]] = data.get("channel_names", "channel{i}")
        size = data.get("size", "#channel_names")
        if size == "#channel_names" and channel_names == "channel{i}":
            raise ValueError("Channel dimension has unknown size. Please specify `size` or `channel_names`.")

        if (
            size == "#channel_names"
            and not isinstance(channel_names, str)
            and isinstance(channel_names, collections.abc.Sequence)
        ):
            data["size"] = len(channel_names)

        if isinstance(channel_names, str) and "{i}" in channel_names and isinstance(size, int):
            data["channel_names"] = [channel_names.format(i=i) for i in range(1, size + 1)]

        return data


class IndexTimeSpaceAxisBase(AxisBase):
    size: Annotated[
        Union[Annotated[int, Gt(0)], ParameterizedSize, SizeReference, AxisId, TensorAxisId],
        Field(
            examples=[
                10,
                "other_axis",
                ParameterizedSize(min=32, step=16).model_dump(),
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


class IndexAxis(IndexTimeSpaceAxisBase):
    type: Literal["index"] = "index"
    id: AxisId = AxisId("index")


class TimeAxisBase(IndexTimeSpaceAxisBase):
    type: Literal["time"] = "time"
    id: AxisId = AxisId("time")
    unit: Optional[TimeUnit] = None
    scale: Annotated[float, Gt(0)] = 1.0


class TimeInputAxis(TimeAxisBase):
    pass


class SpaceAxisBase(IndexTimeSpaceAxisBase):
    type: Literal["space"] = "space"
    id: Annotated[AxisId, Field(examples=["x", "y", "z"])] = AxisId("x")
    unit: Optional[SpaceUnit] = None
    scale: Annotated[float, Gt(0)] = 1.0


class SpaceInputAxis(SpaceAxisBase):
    pass


InputAxis = Annotated[
    Union[BatchAxis, ChannelAxis, IndexAxis, TimeInputAxis, SpaceInputAxis], Field(discriminator="type")
]


class TimeOutputAxis(TimeAxisBase, WithHalo):
    pass


class SpaceOutputAxis(SpaceAxisBase, WithHalo):
    pass


OutputAxis = Annotated[
    Union[BatchAxis, ChannelAxis, IndexAxis, TimeOutputAxis, SpaceOutputAxis], Field(discriminator="type")
]

AnyAxis = Union[InputAxis, OutputAxis]

TVs = Union[NotEmpty[List[int]], NotEmpty[List[float]], NotEmpty[List[bool]], NotEmpty[List[str]]]


NominalOrOrdinalDType = Literal[
    "float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64", "bool"
]


class NominalOrOrdinalDataDescr(Node):
    values: TVs
    """A fixed set of nominal or an ascending sequence of ordinal values.
    In this case `data_type` is required to be an unsigend integer type, e.g. 'uint8'.
    String `values` are interpreted as labels for tensor values 0, ..., N.
    Note: as YAML 1.2 does not natively support a "set" datatype,
    nominal values should be given as a sequence (aka list/array) as well.
    """

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

    unit: Optional[Union[Literal["arbitrary unit"], SiUnit]] = None

    @property
    def range(self):
        if isinstance(self.values[0], str):
            return 0, len(self.values) - 1
        else:
            return min(self.values), max(self.values)


IntervalOrRatioDType = Literal[
    "float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64"
]


class IntervalOrRatioDataDescr(Node):
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
    unit: Union[Literal["arbitrary unit"], SiUnit] = "arbitrary unit"
    scale: float = 1.0
    """Scale for data on an interval (or ratio) scale."""
    offset: Optional[float] = None
    """Offset for data on a ratio scale."""


TensorDataDescr = Union[NominalOrOrdinalDataDescr, IntervalOrRatioDataDescr]


class ProcessingDescrBase(NodeWithExplicitlySetFields, ABC):
    """processing base class"""

    # id: Literal[PreprocessingId, PostprocessingId]  # make abstract field
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset({"id"})


class BinarizeDescr(ProcessingDescrBase):
    """Binarize the tensor with a fixed threshold.
    Values above the threshold will be set to one, values below the threshold to zero."""

    id: Literal["binarize"] = "binarize"
    kwargs: BinarizeKwargs


class ClipDescr(ProcessingDescrBase):
    """Set tensor values below min to min and above max to max."""

    id: Literal["clip"] = "clip"
    kwargs: ClipKwargs


class EnsureDtypeKwargs(ProcessingKwargs):
    dtype: str


class EnsureDtypeDescr(ProcessingDescrBase):
    id: Literal["ensure_dtype"] = "ensure_dtype"
    kwargs: EnsureDtypeKwargs


class ScaleLinearKwargs(ProcessingKwargs):
    axis: Annotated[Optional[NonBatchAxisId], Field(examples=["channel"])] = None  # todo: validate existence of axis
    """The axis of non-scalar gains/offsets.
    Invalid for scalar gains/offsets.
    """

    gain: Union[float, NotEmpty[List[float]]] = 1.0
    """multiplicative factor"""

    offset: Union[float, NotEmpty[List[float]]] = 0.0
    """additive term"""

    @model_validator(mode="after")
    def either_gain_or_offset(self) -> Self:
        if (self.gain == 1.0 or isinstance(self.gain, list) and all(g == 1.0 for g in self.gain)) and (
            self.offset == 0.0 or isinstance(self.offset, list) and all(off == 0.0 for off in self.offset)
        ):
            raise ValueError("Redundant linear scaling not allowd. Set `gain` != 1.0 and/or `offset` != 0.0.")

        return self


class ScaleLinearDescr(ProcessingDescrBase):
    """Fixed linear scaling."""

    id: Literal["scale_linear"] = "scale_linear"
    kwargs: ScaleLinearKwargs


class SigmoidDescr(ProcessingDescrBase):
    """The logistic sigmoid funciton, a.k.a. expit function."""

    id: Literal["sigmoid"] = "sigmoid"

    @property
    def kwargs(self) -> ProcessingKwargs:
        """empty kwargs"""
        return ProcessingKwargs()


class FixedZeroMeanUnitVarianceKwargs(ProcessingKwargs):
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


class FixedZeroMeanUnitVarianceDescr(ProcessingDescrBase):
    """Subtract a given mean and divide by a given variance."""

    id: Literal["fixed_zero_mean_unit_variance"] = "fixed_zero_mean_unit_variance"
    kwargs: FixedZeroMeanUnitVarianceKwargs


class ZeroMeanUnitVarianceKwargs(ProcessingKwargs):
    mode: Literal["per_dataset", "per_sample"] = "per_dataset"
    """Compute percentiles independently ('per_sample') or across many samples ('per_dataset')."""

    axes: Annotated[Optional[Sequence[NonBatchAxisId]], Field(examples=[("x", "y")])] = None
    """The subset of non-batch axes to normalize jointly, i.e. axes to reduce to compute mean/std.
    For example to normalize 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('x', 'y')`.
    The batch axis cannot be normalized across; use `mode=per_dataset` to normalize samples jointly
    or `mode=per_sample` to normalize samples independently.
    Default: Scale all non-batch axes jointly."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`."""


class ZeroMeanUnitVarianceDescr(ProcessingDescrBase):
    """Subtract mean and divide by variance."""

    id: Literal["zero_mean_unit_variance"] = "zero_mean_unit_variance"
    kwargs: ZeroMeanUnitVarianceKwargs


class ScaleRangeKwargs(ProcessingKwargs):
    mode: Literal["per_dataset", "per_sample"] = "per_dataset"
    """Compute percentiles independently ('per_sample') or across many samples ('per_dataset')."""

    axes: Annotated[Optional[Sequence[NonBatchAxisId]], Field(examples=[("x", "y")])] = None
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
    def min_smaller_max(cls, value: float, info: ValidationInfo) -> float:
        if (min_p := info.data["min_percentile"]) >= value:
            raise ValueError(f"min_percentile {min_p} >= max_percentile {value}")

        return value


class ScaleRangeDescr(ProcessingDescrBase):
    """Scale with percentiles."""

    id: Literal["scale_range"] = "scale_range"
    kwargs: ScaleRangeKwargs


class ScaleMeanVarianceKwargs(ProcessingKwargs):
    """Scale a tensor's data distribution to match another tensor's mean/std.
    `out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean.`"""

    mode: Literal["per_dataset", "per_sample"] = "per_dataset"
    """Compute percentiles independently ('per_sample') or across many samples ('per_dataset')."""
    reference_tensor: TensorId
    """Name of tensor to match."""

    axes: Annotated[Optional[Sequence[NonBatchAxisId]], Field(examples=[("x", "y")])] = None
    """The subset of non-batch axes to normalize jointly, i.e. axes to reduce to compute mean/std.
    For example to normalize 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('x', 'y')`.
    The batch axis cannot be normalized across; use `mode=per_dataset` to normalize samples jointly
    or `mode=per_sample` to normalize samples independently.
    Default: Scale all non-batch axes jointly."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """Epsilon for numeric stability:
    `out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean.`"""


class ScaleMeanVarianceDescr(ProcessingDescrBase):
    """Scale the tensor s.t. its mean and variance match a reference tensor."""

    id: Literal["scale_mean_variance"] = "scale_mean_variance"
    kwargs: ScaleMeanVarianceKwargs


PreprocessingDescr = Annotated[
    Union[
        BinarizeDescr,
        ClipDescr,
        EnsureDtypeDescr,
        ScaleLinearDescr,
        SigmoidDescr,
        FixedZeroMeanUnitVarianceDescr,
        ZeroMeanUnitVarianceDescr,
        ScaleRangeDescr,
    ],
    Field(discriminator="id"),
]
PostprocessingDescr = Annotated[
    Union[
        BinarizeDescr,
        ClipDescr,
        EnsureDtypeDescr,
        ScaleLinearDescr,
        SigmoidDescr,
        FixedZeroMeanUnitVarianceDescr,
        ZeroMeanUnitVarianceDescr,
        ScaleRangeDescr,
        ScaleMeanVarianceDescr,
    ],
    Field(discriminator="id"),
]

AxisVar = TypeVar("AxisVar", InputAxis, OutputAxis)


class TensorDescrBase(Node, Generic[AxisVar]):
    id: TensorId
    """Tensor id. No duplicates are allowed."""

    description: Annotated[str, MaxLen(128)] = ""
    """free text description"""

    axes: NotEmpty[Sequence[AxisVar]]
    """tensor axes"""

    @property
    def shape(self):
        return tuple(a.size for a in self.axes)

    @field_validator("axes", mode="after", check_fields=False)
    @classmethod
    def validate_axes(cls, axes: Sequence[AnyAxis]) -> Sequence[AnyAxis]:
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

    test_tensor: FileDescr
    """∈📦 An example tensor to use for testing.
    Using the model with the test input tensors is expected to yield the test output tensors.
    Each test tensor has be a an ndarray in the
    [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
    The file extension must be '.npy'."""

    sample_tensor: Optional[FileDescr] = None
    """∈📦 A sample tensor to illustrate a possible input/output for the model,
    The sample image primarily serves to inform a human user about an example use case
    and is typically stored as .hdf5, .png or .tiff.
    It has to be readable by the [imageio library](https://imageio.readthedocs.io/en/stable/formats/index.html#supported-formats).
    And the image dimensionality has to match the number of axes specified in this tensor description.
    """

    @model_validator(mode="after")
    def validate_sample_tensor(self, info: ValidationInfo) -> Self:
        if self.sample_tensor is None:
            return self

        context = get_internal_validation_context(info.context)
        if not context["perform_io_checks"]:
            return self

        down = download(self.sample_tensor.source, sha256=self.sample_tensor.sha256)

        local_source = down.path
        tensor: NDArray[Any] = imread(local_source, extension=PurePosixPath(down.original_file_name).suffix)
        n_dims = len(tensor.squeeze().shape)
        n_dims_min = n_dims_max = len(self.axes)

        for a in self.axes:
            if isinstance(a, BatchAxis):
                n_dims_min -= 1
            elif isinstance(a.size, int) and a.size == 1:
                n_dims_min -= 1
            elif isinstance(a.size, ParameterizedSize):
                if a.size.min == 1:
                    n_dims_min -= 1
            elif isinstance(a.size, (SizeReference, str)):
                # TODO: validate with known other tensor sizes if this axis may be a singleton axis
                n_dims_min -= 1

        n_dims_min = max(0, n_dims_min)
        if n_dims < n_dims_min or n_dims > n_dims_max:
            raise ValueError(
                f"Expected sample tensor to have {n_dims_min} to {n_dims_max} dimensions, "
                f"but found {n_dims} (shape: {tensor.shape})."
            )

        return self

    data: Union[TensorDataDescr, NotEmpty[Sequence[TensorDataDescr]]] = IntervalOrRatioDataDescr()
    """Description of the tensor's data values, optionally per channel.
    If specified per channel, the data `type` needs to match across channels."""

    @property
    def dtype(
        self,
    ) -> Literal[
        "float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64", "bool"
    ]:
        """dtype as specified under `data.type` or `data[i].type`"""
        if isinstance(self.data, collections.abc.Sequence):
            return self.data[0].type
        else:
            return self.data.type

    @field_validator("data", mode="after")
    @classmethod
    def check_data_type_across_channels(
        cls, value: Union[TensorDataDescr, NotEmpty[Sequence[TensorDataDescr]]]
    ) -> Union[TensorDataDescr, NotEmpty[Sequence[TensorDataDescr]]]:
        if not isinstance(value, list):
            return value

        dtypes = {t.type for t in value}
        if len(dtypes) > 1:
            raise ValueError(
                f"Tensor data descriptions per channel need to agree in their data `type`, but found {dtypes}."
            )

        return value

    @model_validator(mode="after")
    def check_data_matches_channelaxis(self) -> Union[Self, InputTensorDescr, OutputTensorDescr]:
        if not isinstance(self.data, list) or not isinstance(self, (InputTensorDescr, OutputTensorDescr)):
            return self

        for a in self.axes:
            if isinstance(a, ChannelAxis):
                size = a.size
                assert isinstance(size, int)
                break
        else:
            return self

        if len(self.data) != size:
            raise ValueError(
                f"Got tensor data descriptions for {len(self.data)} channels, but '{a.id}' axis has size {size}."
            )

        return self

    def get_axis_sizes(self, tensor: NDArray[Any]) -> Dict[AxisId, int]:
        if len(tensor.shape) != len(self.axes):
            raise ValueError(
                f"Dimension mismatch: array shape {tensor.shape} (#{len(tensor.shape)}) "
                f"incompatible with {len(self.axes)} axes."
            )
        return {a.id: tensor.shape[i] for i, a in enumerate(self.axes)}

    def validate_tensor(
        self,
        tensor: NDArray[Any],
        *,
        other_known_tensor_sizes: Optional[Mapping[TensorId, Mapping[AxisId, int]]] = None,
    ) -> NDArray[Any]:
        known_tensor_sizes = dict(other_known_tensor_sizes or {})
        known_tensor_sizes[self.id] = self.get_axis_sizes(tensor)

        if tensor.dtype.name != self.dtype:
            raise ValueError(f"tensor with dtype {tensor.dtype.name} does not match specified dtype {self.dtype}")

        shape = list(tensor.shape)
        for i, a in enumerate(self.axes):
            if a.size is None:
                continue

            if isinstance(a.size, str):
                size = SizeReference(reference=a.size)
            else:
                size = a.size

            if isinstance(size, int):
                if shape[i] != size:
                    raise ValueError(f"incompatible shape: array.shape[{i}] = {shape[i]} != {size}")
            elif isinstance(size, ParameterizedSize):
                _ = size.validate_size(shape[i])
            elif isinstance(size, SizeReference):  # pyright: ignore[reportUnnecessaryIsInstance]
                _ = size.validate_size(shape[i], tensor_id=self.id, known_tensor_sizes=known_tensor_sizes)
            else:
                assert_never(size)

        return tensor


class InputTensorDescr(TensorDescrBase[InputAxis]):
    id: TensorId = TensorId("input")
    """Input tensor id.
    No duplicates are allowed across all inputs and outputs."""

    preprocessing: List[PreprocessingDescr] = Field(default_factory=list)
    """Description of how this input should be preprocessed."""

    @model_validator(mode="after")
    def validate_preprocessing_kwargs(self) -> Self:
        axes_ids = [a.id for a in self.axes]
        for p in self.preprocessing:
            kwargs_axes: Union[Any, Sequence[Any]] = p.kwargs.get("axes", ())
            if not isinstance(kwargs_axes, collections.abc.Sequence):
                raise ValueError(f"Expeted `axes` to be a sequence, but got {type(kwargs_axes)}")

            if any(a not in axes_ids for a in kwargs_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes ids")

        return self


class OutputTensorDescr(TensorDescrBase[OutputAxis]):
    id: TensorId = TensorId("output")
    """Output tensor id.
    No duplicates are allowed across all inputs and outputs."""

    postprocessing: List[PostprocessingDescr] = Field(default_factory=list)
    """Description of how this output should be postprocessed."""

    @model_validator(mode="after")
    def validate_postprocessing_kwargs(self) -> Self:
        axes_ids = [a.id for a in self.axes]
        for p in self.postprocessing:
            kwargs_axes: Union[Any, Sequence[Any]] = p.kwargs.get("axes", ())
            if not isinstance(kwargs_axes, collections.abc.Sequence):
                raise ValueError(f"expected `axes` sequence, but got {type(kwargs_axes)}")

            if any(a not in axes_ids for a in kwargs_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes ids")

        return self


TensorDescr = Union[InputTensorDescr, OutputTensorDescr]


class EnvironmentFileDescr(FileDescr):
    source: Annotated[
        FileSource, WithSuffix((".yaml", ".yml"), case_sensitive=True), Field(examples=["environment.yaml"])
    ]
    """∈📦 Conda environment file.
    Allows to specify custom dependencies, see conda docs:
    - [Exporting an environment file across platforms](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#exporting-an-environment-file-across-platforms)
    - [Creating an environment file manually](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually)
    """


class _ArchitectureCallableDescr(Node):
    callable: Annotated[Identifier, Field(examples=["MyNetworkClass", "get_my_model"])]
    """Identifier of the callable that returns a torch.nn.Module instance."""

    kwargs: Dict[str, Any] = Field(default_factory=dict)
    """key word arguments for the `callable`"""


class ArchitectureFromFileDescr(_ArchitectureCallableDescr, FileDescr):
    pass


class ArchitectureFromLibraryDescr(_ArchitectureCallableDescr):
    import_from: str
    """Where to import the callable from, i.e. `from <import_from> import <callable>`"""


ArchitectureDescr = Union[ArchitectureFromFileDescr, ArchitectureFromLibraryDescr]


class WeightsEntryDescrBase(FileDescr):
    type: ClassVar[WeightsFormat]
    weights_format_name: ClassVar[str]  # human readable

    source: FileSource
    """∈📦 The weights file."""

    authors: Optional[List[Author]] = None
    """Authors
    Either the person(s) that have trained this model resulting in the original weights file.
        (If this is the initial weights entry, i.e. it does not have a `parent`)
    Or the person(s) who have converted the weights to this weights format.
        (If this is a child weight, i.e. it has a `parent` field)
    """

    parent: Annotated[Optional[WeightsFormat], Field(examples=["pytorch_state_dict"])] = None
    """The source weights these weights were converted from.
    For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
    The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
    All weight entries except one (the initial set of weights resulting from training the model),
    need to have this field."""

    @model_validator(mode="after")
    def check_parent_is_not_self(self) -> Self:
        if self.type == self.parent:
            raise ValueError("Weights entry can't be it's own parent.")

        return self


class KerasHdf5WeightsDescr(WeightsEntryDescrBase):
    type = "keras_hdf5"
    weights_format_name: ClassVar[str] = "Keras HDF5"
    tensorflow_version: Version  # todo: dynamic default from tf lib
    """TensorFlow version used to create these weights."""


class OnnxWeightsDescr(WeightsEntryDescrBase):
    type = "onnx"
    weights_format_name: ClassVar[str] = "ONNX"
    opset_version: Annotated[int, Ge(7)]  # todo: dynamic default from onnx runtime
    """ONNX opset version"""


class PytorchStateDictWeightsDescr(WeightsEntryDescrBase):
    type = "pytorch_state_dict"
    weights_format_name: ClassVar[str] = "Pytorch State Dict"
    architecture: ArchitectureDescr
    pytorch_version: Version
    """Version of the PyTorch library used.
    If `architecture.depencencies` is specified it has to include pytorch and any version pinning has to be compatible.
    """
    dependencies: Optional[EnvironmentFileDescr] = None
    """Custom depencies beyond pytorch.
    The conda environment file should include pytorch and any version pinning has to be compatible with
    `pytorch_version`.
    """


class TensorflowJsWeightsDescr(WeightsEntryDescrBase):
    type = "tensorflow_js"
    weights_format_name: ClassVar[str] = "Tensorflow.js"
    tensorflow_version: Version
    """Version of the TensorFlow library used."""

    source: FileSource
    """∈📦 The multi-file weights.
    All required files/folders should be a zip archive."""


class TensorflowSavedModelBundleWeightsDescr(WeightsEntryDescrBase):
    type = "tensorflow_saved_model_bundle"
    weights_format_name: ClassVar[str] = "Tensorflow Saved Model"
    tensorflow_version: Version
    """Version of the TensorFlow library used."""

    dependencies: Optional[EnvironmentFileDescr] = None
    """Custom dependencies beyond tensorflow.
    Should include tensorflow and any version pinning has to be compatible with `tensorflow_version`."""

    source: FileSource
    """∈📦 The multi-file weights.
    All required files/folders should be a zip archive."""


class TorchscriptWeightsDescr(WeightsEntryDescrBase):
    type = "torchscript"
    weights_format_name: ClassVar[str] = "TorchScript"
    pytorch_version: Version
    """Version of the PyTorch library used."""


class WeightsDescr(Node):
    keras_hdf5: Optional[KerasHdf5WeightsDescr] = None
    onnx: Optional[OnnxWeightsDescr] = None
    pytorch_state_dict: Optional[PytorchStateDictWeightsDescr] = None
    tensorflow_js: Optional[TensorflowJsWeightsDescr] = None
    tensorflow_saved_model_bundle: Optional[TensorflowSavedModelBundleWeightsDescr] = None
    torchscript: Optional[TorchscriptWeightsDescr] = None

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


class ModelDescr(GenericModelDescrBase, title="bioimage.io model specification"):
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

    authors: NotEmpty[List[Author]]
    """The authors are the creators of the model RDF and the primary points of contact."""

    documentation: Annotated[
        MarkdownSource,
        Field(
            examples=[
                "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/README.md",
                "README.md",
            ],
        ),
    ]
    """∈📦 URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
    The documentation should include a '#[#] Validation' (sub)section
    with details on how to quantitatively validate the model on unseen data."""

    inputs: NotEmpty[Sequence[InputTensorDescr]]
    """Describes the input tensors expected by this model."""

    @field_validator("inputs", mode="after")
    @classmethod
    def validate_input_axes(cls, inputs: Sequence[InputTensorDescr]) -> Sequence[InputTensorDescr]:
        input_size_refs = cls._get_axes_with_independent_size(inputs)

        for i, ipt in enumerate(inputs):
            valid_independent_refs: Dict[
                Union[AxisId, TensorAxisId], Tuple[TensorDescr, AnyAxis, Union[int, ParameterizedSize]]
            ] = {
                **{
                    a.id: (ipt, a, a.size)
                    for a in ipt.axes
                    if not isinstance(a, BatchAxis) and isinstance(a.size, (int, ParameterizedSize))
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
        valid_independent_refs: Dict[
            Union[AxisId, TensorAxisId], Tuple[TensorDescr, AnyAxis, Union[int, ParameterizedSize]]
        ],
    ):
        if isinstance(axis, BatchAxis) or isinstance(axis.size, int):
            return

        if (
            isinstance(axis.size, ParameterizedSize)
            and isinstance(axis, WithHalo)
            and (axis.size.min - 2 * axis.halo) < 1
        ):
            raise ValueError(f"axis {axis.id} with minimum size {axis.size.min} is too small for halo {axis.halo}.")

        if isinstance(axis.size, SizeReference):
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
            if axis.type == "channel":
                if valid_independent_refs[axis.size.reference][1].type != "channel":
                    raise ValueError("A channel axis' size may only reference another fixed size channel axis.")
                if isinstance(axis.channel_names, str) and "{i}" in axis.channel_names:
                    ref_size = valid_independent_refs[axis.size.reference][2]
                    assert isinstance(
                        ref_size, int
                    ), "channel axis ref (another channel axis) has to specify fixed size"
                    generated_channel_names = [
                        Identifier(axis.channel_names.format(i=i)) for i in range(1, ref_size + 1)
                    ]
                    axis.channel_names = generated_channel_names

            if (ax_unit := getattr(axis, "unit", None)) != (
                ref_unit := getattr(valid_independent_refs[axis.size.reference][1], "unit", None)
            ):
                raise ValueError(
                    f"The units of an axis and its reference axis need to match, but '{ax_unit}' != '{ref_unit}'."
                )
            min_size = valid_independent_refs[axis.size.reference][2]
            if isinstance(min_size, ParameterizedSize):
                min_size = min_size.min

            if isinstance(axis, WithHalo) and (min_size - 2 * axis.halo) < 1:
                raise ValueError(f"axis {axis.id} with minimum size {min_size} is too small for halo {axis.halo}.")

        elif isinstance(axis.size, str):
            if axis.size not in valid_independent_refs:
                raise ValueError(f"Invalid tensor axis reference at {field_name}[{i}].axes[{a}].size: {axis.size}.")
            if axis.size in (axis.id, f"{tensor_id}.{axis.id}"):
                raise ValueError(f"Self-referencing not allowed for {field_name}[{i}].axes[{a}].size: {axis.size}.")
            if axis.type == "channel":
                if valid_independent_refs[axis.size][1].type != "channel":
                    raise ValueError("A channel axis' size may only reference another fixed size channel axis.")
                if isinstance(axis.channel_names, str) and "{i}" in axis.channel_names:
                    ref_size = valid_independent_refs[axis.size][2]
                    assert isinstance(
                        ref_size, int
                    ), "channel axis ref (another channel axis) has to specify fixed size"
                    generated_channel_names = [
                        Identifier(axis.channel_names.format(i=i)) for i in range(1, ref_size + 1)
                    ]
                    axis.channel_names = generated_channel_names

    @model_validator(mode="after")
    def validate_test_tensors(self, info: ValidationInfo) -> Self:
        context = get_internal_validation_context(info.context)
        if not context["perform_io_checks"]:
            return self

        ipt_test_arrays = [load_array(ipt.test_tensor.download().path) for ipt in self.inputs]
        known_sizes = {ipt.id: ipt.get_axis_sizes(ta) for ipt, ta in zip(self.inputs, ipt_test_arrays)}

        for i, ipt in enumerate(self.inputs):
            try:
                _ = ipt.validate_tensor(ipt_test_arrays[i], other_known_tensor_sizes=known_sizes)
            except ValueError as e:
                raise ValueError(f"inputs[{i}].test_tensor: {e}") from e  # TODO: raise error with correct location

        out_test_arrays = [load_array(out.test_tensor.download().path) for out in self.outputs]
        known_sizes.update({out.id: out.get_axis_sizes(ta) for out, ta in zip(self.outputs, out_test_arrays)})

        for i, out in enumerate(self.outputs):
            try:
                _ = out.validate_tensor(out_test_arrays[i], other_known_tensor_sizes=known_sizes)
            except ValueError as e:
                raise ValueError(f"outputs[{i}].test_tensor: {e}") from e  # TODO: raise error with correct location

        return self

    # TODO: use validate funcs in validate_test_tensors
    # def validate_inputs(self, input_tensors: Mapping[TensorId, NDArray[Any]]) -> Mapping[TensorId, NDArray[Any]]:

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

    outputs: NotEmpty[List[OutputTensorDescr]]
    """Describes the output tensors."""

    @field_validator("outputs", mode="after")
    @classmethod
    def validate_tensor_ids(cls, outputs: List[OutputTensorDescr], info: ValidationInfo) -> List[OutputTensorDescr]:
        tensor_ids = [t.id for t in info.data.get("inputs", []) + info.data.get("outputs", [])]
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
    def _get_axes_with_parameterized_size(io: Union[Sequence[InputTensorDescr], Sequence[OutputTensorDescr]]):
        return {
            f"{t.id}.{a.id}": (t, a, a.size)
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis) and isinstance(a.size, ParameterizedSize)
        }

    @staticmethod
    def _get_axes_with_independent_size(io: Union[Sequence[InputTensorDescr], Sequence[OutputTensorDescr]]):
        return {
            f"{t.id}.{a.id}": (t, a, a.size)
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis) and isinstance(a.size, (int, ParameterizedSize))
        }

    @field_validator("outputs", mode="after")
    @classmethod
    def validate_output_axes(cls, outputs: List[OutputTensorDescr], info: ValidationInfo) -> List[OutputTensorDescr]:
        input_size_refs = cls._get_axes_with_independent_size(info.data.get("inputs", []))
        output_size_refs = cls._get_axes_with_independent_size(outputs)

        for i, out in enumerate(outputs):
            valid_independent_refs: Dict[
                Union[AxisId, TensorAxisId], Tuple[TensorDescr, AnyAxis, Union[int, ParameterizedSize]]
            ] = {
                **{
                    a.id: (out, a, a.size)
                    for a in out.axes
                    if not isinstance(a, BatchAxis) and isinstance(a.size, (int, ParameterizedSize))
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
                    valid_independent_refs=valid_independent_refs,
                )

        return outputs

    packaged_by: List[Author] = Field(default_factory=list)
    """The persons that have packaged and uploaded this model.
    Only required if those persons differ from the `authors`."""

    parent: Optional[LinkedModel] = None
    """The model from which this model is derived, e.g. by fine-tuning the weights."""

    # todo: add parent self check once we have `id`
    # @model_validator(mode="after")
    # def validate_parent_is_not_self(self) -> Self:
    #     if self.parent is not None and self.parent == self.id:
    #         raise ValueError("The model may not reference itself as parent model")

    #     return self

    run_mode: Annotated[
        Optional[RunMode], warn(None, "Run mode '{value}' has limited support across consumer softwares.")
    ] = None
    """Custom run mode for this model: for more complex prediction procedures like test time
    data augmentation that currently cannot be expressed in the specification.
    No standard run modes are defined yet."""

    timestamp: Datetime = datetime.now()
    """Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
    with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat).
    (In Python a datetime object is valid, too)."""

    training_data: Union[LinkedDatasetDescr, DatasetDescr, None] = None
    """The dataset used to train this model"""

    weights: WeightsDescr
    """The weights for this model.
    Weights can be given for different formats, but should otherwise be equivalent.
    The available weight formats determine which consumers can use this model."""

    @model_validator(mode="after")
    def add_default_cover(self, info: ValidationInfo) -> Self:
        context = get_internal_validation_context(info.context)
        if not context["perform_io_checks"] or self.covers:
            return self

        try:
            from bioimageio.spec._internal.cover import generate_covers

            generated_covers = generate_covers(
                [(t, load_array(t.test_tensor.download().path)) for t in self.inputs],
                [(t, load_array(t.test_tensor.download().path)) for t in self.outputs],
            )
        except Exception as e:
            issue_warning(
                "Failed to generate cover image(s): {e}", value=self.covers, val_context=context, msg_context=dict(e=e)
            )
        else:
            self.covers.extend(generated_covers)

        return self

    @classmethod
    def convert_from_older_format(cls, data: BioimageioYamlContent, context: InternalValidationContext) -> None:
        convert_from_older_format(data, context)

    def get_input_test_arrays(self) -> List[NDArray[Any]]:
        data = [load_array(ipt.test_tensor.download().path) for ipt in self.inputs]
        assert all(isinstance(d, np.ndarray) for d in data)
        return data

    def get_output_test_arrays(self) -> List[NDArray[Any]]:
        data = [load_array(out.test_tensor.download().path) for out in self.outputs]
        assert all(isinstance(d, np.ndarray) for d in data)
        return data
