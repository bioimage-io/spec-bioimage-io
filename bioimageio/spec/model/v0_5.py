from __future__ import annotations

import collections.abc
from abc import ABC
from datetime import datetime
from itertools import chain
from pathlib import PurePosixPath
from typing import (
    TYPE_CHECKING,
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
    cast,
)

import numpy as np
from annotated_types import Ge, Gt, Interval, MaxLen, MinLen, Predicate
from imageio.v3 import imread  # pyright: ignore[reportUnknownVariableType]
from numpy.typing import NDArray
from packaging.version import Version as Version
from pydantic import (
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated, LiteralString, Self, assert_never

from bioimageio.spec._internal.base_nodes import Converter, InvalidDescription, Node, NodeWithExplicitlySetFields
from bioimageio.spec._internal.constants import DTYPE_LIMITS, INFO
from bioimageio.spec._internal.field_warning import issue_warning, warn
from bioimageio.spec._internal.io_utils import download, load_array
from bioimageio.spec._internal.types import BioimageioYamlContent as BioimageioYamlContent
from bioimageio.spec._internal.types import Datetime as Datetime
from bioimageio.spec._internal.types import DeprecatedLicenseId as DeprecatedLicenseId
from bioimageio.spec._internal.types import HttpUrl as HttpUrl
from bioimageio.spec._internal.types import Identifier as Identifier
from bioimageio.spec._internal.types import ImportantFileSource, LowerCaseIdentifierStr, SiUnit
from bioimageio.spec._internal.types import LicenseId as LicenseId
from bioimageio.spec._internal.types import NotEmpty as NotEmpty
from bioimageio.spec._internal.types import ResourceId as ResourceId
from bioimageio.spec._internal.types import Sha256 as Sha256
from bioimageio.spec._internal.types import Version as _Version
from bioimageio.spec._internal.types.field_validation import WithSuffix
from bioimageio.spec._internal.validation_context import validation_context_var
from bioimageio.spec.dataset.v0_3 import DatasetDescr as DatasetDescr
from bioimageio.spec.dataset.v0_3 import LinkedDatasetDescr as LinkedDatasetDescr
from bioimageio.spec.generic.v0_3 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import (
    DocumentationSource,
    GenericModelDescrBase,
    _author_conv,  # pyright: ignore[reportPrivateUsage]
    _maintainer_conv,  # pyright: ignore[reportPrivateUsage]
)
from bioimageio.spec.generic.v0_3 import Doi as Doi
from bioimageio.spec.generic.v0_3 import FileDescr as FileDescr
from bioimageio.spec.generic.v0_3 import LinkedResourceDescr as LinkedResourceDescr
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3 import OrcidId as OrcidId
from bioimageio.spec.generic.v0_3 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.model import v0_4
from bioimageio.spec.model.v0_4 import BinarizeKwargs as BinarizeKwargs
from bioimageio.spec.model.v0_4 import CallableFromDepencency as CallableFromDepencency
from bioimageio.spec.model.v0_4 import ClipKwargs as ClipKwargs
from bioimageio.spec.model.v0_4 import KnownRunMode as KnownRunMode
from bioimageio.spec.model.v0_4 import LinkedModel as LinkedModel
from bioimageio.spec.model.v0_4 import ProcessingKwargs as ProcessingKwargs
from bioimageio.spec.model.v0_4 import RunMode as RunMode
from bioimageio.spec.model.v0_4 import WeightsFormat as WeightsFormat

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


NonBatchAxisId = Annotated[AxisId, Predicate(lambda x: x != "batch")]

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

    def validate_size(self, size: int) -> int:
        if size < self.min:
            raise ValueError(f"size {size} < {self.min}")
        if (size - self.min) % self.step != 0:
            raise ValueError(
                f"axis of size {size} is not parametrized by `min + n*step` = `{self.min} + n*{self.step}`"
            )

        return size


class SizeReference(Node):
    """A tensor axis size (extent in pixels/frames) defined in relation to a reference axis.

    `axis.size = reference.size * reference.scale / axis.scale + offset`

    note:
    1. The axis and the referenced axis need to have the same unit (or no unit).
    2. Batch axes may not be referenced.
    3. Fractions are rounded down.

    example:
    An unisotropic input image of w*h=100*49 pixels depicts a phsical space of 200*196mm².
    Let's assume that we want to express the image height h in relation to its width w
    instead of only accepting input images of exactly 100*49 pixels
    (for example to express a range of valid image shapes by parametrizing w, see `ParametrizedSize`).

    >>> w = SpaceInputAxis(id=AxisId("w"), size=100, unit="millimeter", scale=2)
    >>> h = SpaceInputAxis(
    ...     id=AxisId("h"),
    ...     size=SizeReference(tensor_id=TensorId("input"), axis_id=AxisId("w"), offset=-1),
    ...     unit="millimeter",
    ...     scale=4,
    ... )
    >>> print(h.size.compute(h, w))
    49

    -> h = w * w.scale / h.scale + offset = 100 * 2mm / 4mm - 1 = 49
    """

    tensor_id: TensorId
    """tensor id of the reference axis"""

    axis_id: AxisId
    """axis id of the reference axis"""

    offset: int = 0

    def compute(
        self,
        axis: Union[ChannelAxis, IndexAxis, TimeInputAxis, SpaceInputAxis, TimeOutputAxis, SpaceOutputAxis],
        ref_axis: Union[ChannelAxis, IndexAxis, TimeInputAxis, SpaceInputAxis, TimeOutputAxis, SpaceOutputAxis],
        n: int = 0,
    ):
        """helper method to compute concrete size for a given axis and its reference axis.
        If the reference axis is parametrized, `n` is used to compute the concrete size of it, see `ParametrizedSize`.
        """
        assert axis.size == self, "Given `axis.size` is not defined by this `SizeReference`"

        assert ref_axis.id == self.axis_id, f"Expected `ref_axis.id` to be {self.axis_id}, but got {ref_axis.id}."

        assert (unit := self._get_unit(axis)) == (
            ref_unit := self._get_unit(ref_axis)
        ), f"`SizeReference` requires `axis` and `ref_axis` to have the same `unit`, but {unit}!={ref_unit}"

        if isinstance(ref_axis.size, (int, float)):
            ref_size = ref_axis.size
        elif isinstance(ref_axis.size, ParameterizedSize):
            ref_size = ref_axis.size.min + ref_axis.size.step * n
        elif isinstance(ref_axis.size, SizeReference):
            raise ValueError(
                "Reference axis referenced in `SizeReference` may not be sized by a `SizeReference` itself."
            )
        else:
            assert_never(ref_axis.size)

        return int(ref_size * ref_axis.scale / axis.scale + self.offset)

    @staticmethod
    def _get_unit(axis: Union[ChannelAxis, IndexAxis, TimeInputAxis, SpaceInputAxis, TimeOutputAxis, SpaceOutputAxis]):
        if isinstance(axis, (ChannelAxis, IndexAxis)):
            return None
        else:
            return axis.unit


# this Axis definition is compatible with the NGFF draft from July 10, 2023
# https://ngff.openmicroscopy.org/latest/#axes-md
class AxisBase(NodeWithExplicitlySetFields):
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset({"type"})

    id: AxisId
    """An axis id unique across all axes of one tensor."""

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

    @property
    def scale(self):
        return 1.0

    @property
    def unit(self):
        return None


class ChannelAxis(AxisBase):
    type: Literal["channel"] = "channel"
    id: NonBatchAxisId = AxisId("channel")
    channel_names: List[Identifier]

    @property
    def size(self) -> int:
        return len(self.channel_names)

    @property
    def scale(self) -> float:
        return 1.0

    @property
    def unit(self):
        return None


class IndexTimeSpaceAxisBase(AxisBase):
    size: Annotated[
        Union[Annotated[int, Gt(0)], ParameterizedSize, SizeReference],
        Field(
            examples=[
                10,
                ParameterizedSize(min=32, step=16).model_dump(),
                SizeReference(tensor_id=TensorId("t"), axis_id=AxisId("a"), offset=5).model_dump(),
            ]
        ),
    ]
    """The size/length of an axis can be specified as
    - fixed integer
    - parametrized series of valid sizes (`ParametrizedSize`)
    - reference to another axis with an optional offset (`SizeReference`)
    """


class IndexAxis(IndexTimeSpaceAxisBase):
    type: Literal["index"] = "index"
    id: NonBatchAxisId = AxisId("index")

    @property
    def scale(self) -> float:
        return 1.0

    @property
    def unit(self):
        return None


class TimeAxisBase(IndexTimeSpaceAxisBase):
    type: Literal["time"] = "time"
    id: NonBatchAxisId = AxisId("time")
    unit: Optional[TimeUnit] = None
    scale: Annotated[float, Gt(0)] = 1.0


class TimeInputAxis(TimeAxisBase):
    pass


class SpaceAxisBase(IndexTimeSpaceAxisBase):
    type: Literal["space"] = "space"
    id: Annotated[NonBatchAxisId, Field(examples=["x", "y", "z"])] = AxisId("x")
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
    See `zero_mean_unit_variance` for data dependent normalization."""

    mean: Annotated[Union[float, NotEmpty[Tuple[float, ...]]], Field(examples=[3.14, (1.1, -2.2, 3.3)])]
    """The mean value(s) to normalize with. Specify `axis` for a sequence of `mean` values"""

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
    axes: Annotated[Optional[Sequence[AxisId]], Field(examples=[("batch", "x", "y")])] = None
    """The subset of axes to normalize jointly, i.e. axes to reduce to compute mean/std.
    For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
    To normalize each sample independently leave out the 'batch' axis.
    Default: Scale all axes jointly."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`."""


class ZeroMeanUnitVarianceDescr(ProcessingDescrBase):
    """Subtract mean and divide by variance."""

    id: Literal["zero_mean_unit_variance"] = "zero_mean_unit_variance"
    kwargs: ZeroMeanUnitVarianceKwargs


class ScaleRangeKwargs(ProcessingKwargs):
    axes: Annotated[Optional[Sequence[AxisId]], Field(examples=[("batch", "x", "y")])] = None
    """The subset of axes to normalize jointly, i.e. axes to reduce to compute the min/max percentile value.
    For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
    To normalize samples indepdencently, leave out the "batch" axis.
    Default: Scale all axes jointly."""

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
    For any tensor in `inputs` only input tensor references are allowed."""

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

    reference_tensor: TensorId
    """Name of tensor to match."""

    axes: Annotated[Optional[Sequence[AxisId]], Field(examples=[("batch", "x", "y")])] = None
    """The subset of axes to normalize jointly, i.e. axes to reduce to compute mean/std.
    For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
    To normalize samples independently, leave out the 'batch' axis.
    Default: Scale all axes jointly."""

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
    """An example tensor to use for testing.
    Using the model with the test input tensors is expected to yield the test output tensors.
    Each test tensor has be a an ndarray in the
    [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
    The file extension must be '.npy'."""

    sample_tensor: Optional[FileDescr] = None
    """A sample tensor to illustrate a possible input/output for the model,
    The sample image primarily serves to inform a human user about an example use case
    and is typically stored as .hdf5, .png or .tiff.
    It has to be readable by the [imageio library](https://imageio.readthedocs.io/en/stable/formats/index.html#supported-formats)
    (numpy's `.npy` format is not supported).
    The image dimensionality has to match the number of axes specified in this tensor description.
    """

    @model_validator(mode="after")
    def validate_sample_tensor(self) -> Self:
        if self.sample_tensor is None or not validation_context_var.get().perform_io_checks:
            return self

        down = download(self.sample_tensor.source, sha256=self.sample_tensor.sha256)

        local_source = down.path
        tensor: NDArray[Any] = imread(local_source, extension=PurePosixPath(down.original_file_name).suffix)
        n_dims = len(tensor.squeeze().shape)
        n_dims_min = n_dims_max = len(self.axes)

        for a in self.axes:
            if isinstance(a, BatchAxis):
                n_dims_min -= 1
            elif isinstance(a.size, int):
                if a.size == 1:
                    n_dims_min -= 1
            elif isinstance(a.size, ParameterizedSize):
                if a.size.min == 1:
                    n_dims_min -= 1
            elif isinstance(a.size, SizeReference):
                if a.size.offset < 2:
                    # size reference may result in singleton axis
                    n_dims_min -= 1
            else:
                assert_never(a.size)

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
    def check_data_matches_channelaxis(self) -> Self:
        if not isinstance(self.data, (list, tuple)):
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


def convert_axes(
    axes: str,
    *,
    shape: Union[Sequence[int], v0_4.ParametrizedInputShape, v0_4.ImplicitOutputShape],
    tensor_type: Literal["input", "output"],
    halo: Optional[Sequence[int]],
):
    ret: List[AnyAxis] = []
    for i, a in enumerate(axes):
        axis_type = _AXIS_TYPE_MAP.get(a, a)
        if axis_type == "batch":
            ret.append(BatchAxis())
            continue

        scale = 1.0
        if isinstance(shape, v0_4.ParametrizedInputShape):
            if shape.step[i] == 0:
                size = shape.min[i]
            else:
                size = ParameterizedSize(min=shape.min[i], step=shape.step[i])
        elif isinstance(shape, v0_4.ImplicitOutputShape):
            ref_t = shape.reference_tensor
            if ref_t.count(".") == 1:
                t_id, a_id = ref_t.split(".")
            else:
                t_id = ref_t
                a_id = _AXIS_ID_MAP.get(a, a)

            if not (orig_scale := shape.scale[i]):
                # old way to insert a new axis dimension
                size = int(2 * shape.offset[i])
            else:
                scale = 1 / orig_scale  # TODO: check for correctness
                size = SizeReference(tensor_id=TensorId(t_id), axis_id=AxisId(a_id), offset=int(2 * shape.offset[i]))
        elif isinstance(shape, collections.abc.Sequence):
            size = shape[i]
        else:
            assert_never(shape)

        if axis_type == "time":
            if tensor_type == "input":
                ret.append(TimeInputAxis(size=size, scale=scale))
            else:
                ret.append(TimeOutputAxis(size=size, scale=scale, halo=0 if halo is None else halo[i]))
        elif axis_type == "index":
            ret.append(IndexAxis(size=size))
        elif axis_type == "channel":
            assert not isinstance(size, ParameterizedSize)
            ret.append(ChannelAxis(size=size))
        elif axis_type == "space":
            if tensor_type == "input":
                ret.append(SpaceInputAxis(id=AxisId(a), size=size, scale=scale))
            else:
                ret.append(SpaceOutputAxis(id=AxisId(a), size=size, scale=scale))

    return ret


_AXIS_TYPE_MAP = {
    "b": "batch",
    "t": "time",
    "i": "index",
    "c": "channel",
    "x": "space",
    "y": "space",
    "z": "space",
}

_AXIS_ID_MAP = {
    "b": "batch",
    "t": "time",
    "i": "index",
    "c": "channel",
}


def _axes_letters_to_ids(
    axes: Optional[str],
) -> Optional[List[AxisId]]:
    if axes is None:
        return None
    return [AxisId(_AXIS_ID_MAP.get(a, a)) for a in axes]


def _convert_proc(
    p: Union[v0_4.PreprocessingDescr, v0_4.PostprocessingDescr]
) -> Union[PreprocessingDescr, PostprocessingDescr]:
    if isinstance(p, v0_4.BinarizeDescr):
        return BinarizeDescr(kwargs=BinarizeKwargs(threshold=p.kwargs.threshold))
    elif isinstance(p, v0_4.ClipDescr):
        return ClipDescr(kwargs=ClipKwargs(min=p.kwargs.min, max=p.kwargs.max))
    elif isinstance(p, v0_4.SigmoidDescr):
        return SigmoidDescr()
    elif isinstance(p, v0_4.ScaleLinearDescr):
        axes = _axes_letters_to_ids(p.kwargs.axes)
        if p.kwargs.axes is not None:
            raise NotImplementedError("converting sclae linear with `axes` not implemented")
        return ScaleLinearDescr(kwargs=ScaleLinearKwargs(axis=None, gain=p.kwargs.gain, offset=p.kwargs.offset))
    elif isinstance(p, v0_4.ScaleMeanVarianceDescr):
        return ScaleMeanVarianceDescr(
            kwargs=ScaleMeanVarianceKwargs(
                axes=_axes_letters_to_ids(p.kwargs.axes),
                reference_tensor=TensorId(p.kwargs.reference_tensor),
                eps=p.kwargs.eps,
            )
        )
    elif isinstance(p, v0_4.ZeroMeanUnitVarianceDescr):
        if p.kwargs.mode == "fixed":
            mean = p.kwargs.mean
            assert mean is not None
            if isinstance(mean, list):
                mean = tuple(mean)

            std = p.kwargs.std
            assert std is not None
            if isinstance(std, list):
                std = tuple(std)

            return FixedZeroMeanUnitVarianceDescr(kwargs=FixedZeroMeanUnitVarianceKwargs(mean=mean, std=std))
        else:
            axes = _axes_letters_to_ids(p.kwargs.axes) or []
            if p.kwargs.mode == "per_dataset":
                axes = [AxisId("batch")] + axes
            if not axes:
                axes = None
            return ZeroMeanUnitVarianceDescr(kwargs=ZeroMeanUnitVarianceKwargs(axes=axes, eps=p.kwargs.eps))

    elif isinstance(p, v0_4.ScaleRangeDescr):
        return ScaleRangeDescr(
            kwargs=ScaleRangeKwargs(
                axes=_axes_letters_to_ids(p.kwargs.axes),
                min_percentile=p.kwargs.min_percentile,
                max_percentile=p.kwargs.max_percentile,
                eps=p.kwargs.eps,
            )
        )
    else:
        assert_never(p)


class _InputTensorConv(
    Converter[v0_4.InputTensorDescr, InputTensorDescr, ImportantFileSource, Optional[ImportantFileSource]]
):
    def _convert(
        self,
        src: v0_4.InputTensorDescr,
        tgt: "type[InputTensorDescr] | type[dict[str, Any]]",
        test_tensor: ImportantFileSource,
        sample_tensor: Optional[ImportantFileSource],
    ) -> "InputTensorDescr | dict[str, Any]":
        axes = convert_axes(src.axes, shape=src.shape, tensor_type="input", halo=None)
        prep: List[PreprocessingDescr] = []
        for p in src.preprocessing:
            cp = _convert_proc(p)
            assert not isinstance(cp, ScaleMeanVarianceDescr)
            prep.append(cp)

        return tgt(
            axes=axes,  # type: ignore
            id=TensorId(src.name),
            test_tensor=FileDescr(source=test_tensor),
            sample_tensor=sample_tensor and FileDescr(source=sample_tensor),
            data=dict(type=src.data_type),  # type: ignore
            preprocessing=prep,
        )


_input_tensor_conv = _InputTensorConv(v0_4.InputTensorDescr, InputTensorDescr)


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


class _OutputTensorConv(
    Converter[v0_4.OutputTensorDescr, OutputTensorDescr, ImportantFileSource, Optional[ImportantFileSource]]
):
    def _convert(
        self,
        src: v0_4.OutputTensorDescr,
        tgt: "type[OutputTensorDescr] | type[dict[str, Any]]",
        test_tensor: ImportantFileSource,
        sample_tensor: Optional[ImportantFileSource],
    ) -> "OutputTensorDescr | dict[str, Any]":
        axes = convert_axes(src.axes, shape=src.shape, tensor_type="output", halo=src.halo)
        return tgt(
            axes=axes,  # type: ignore
            id=TensorId(src.name),
            test_tensor=FileDescr(source=test_tensor),
            sample_tensor=sample_tensor and FileDescr(source=sample_tensor),
            data=dict(type=src.data_type),  # type: ignore
            postprocessing=[_convert_proc(p) for p in src.postprocessing],
        )


_output_tensor_conv = _OutputTensorConv(v0_4.OutputTensorDescr, OutputTensorDescr)


TensorDescr = Union[InputTensorDescr, OutputTensorDescr]


def validate_tensors(
    tensors: Mapping[TensorId, Tuple[TensorDescr, NDArray[Any]]],
    tensor_origin: str,  # for more precise error messages, e.g. 'test_tensor'
):
    all_tensor_axes: Dict[TensorId, Dict[AxisId, Tuple[AnyAxis, int]]] = {}

    def e_msg(d: TensorDescr):
        return f"{'inputs' if isinstance(d, InputTensorDescr) else 'outputs'}[{d.id}]"

    for descr, array in tensors.values():
        try:
            axis_sizes = descr.get_axis_sizes(array)
        except ValueError as e:
            raise ValueError(f"{e_msg(descr)} {e}")
        else:
            all_tensor_axes[descr.id] = {a.id: (a, axis_sizes[a.id]) for a in descr.axes}

    for descr, array in tensors.values():
        if array.dtype.name != descr.dtype:
            raise ValueError(
                f"{e_msg(descr)}.dtype '{array.dtype.name}' does not match described dtype '{descr.dtype}'"
            )

        for a in descr.axes:
            actual_size = all_tensor_axes[descr.id][a.id][1]
            if a.size is None:
                continue

            if isinstance(a.size, int):
                if actual_size != a.size:
                    raise ValueError(
                        f"{e_msg(descr)}.{tensor_origin}: axis '{a.id}' "
                        f"has incompatible size {actual_size}, expected {a.size}"
                    )
            elif isinstance(a.size, ParameterizedSize):
                _ = a.size.validate_size(actual_size)
            elif isinstance(a.size, SizeReference):
                ref_tensor_axes = all_tensor_axes.get(a.size.tensor_id)
                if ref_tensor_axes is None:
                    raise ValueError(
                        f"{e_msg(descr)}.axes[{a.id}].size.tensor_id: Unknown tensor reference '{a.size.tensor_id}'"
                    )

                ref_axis, ref_size = ref_tensor_axes.get(a.size.axis_id, (None, None))
                if ref_axis is None or ref_size is None:
                    raise ValueError(
                        f"{e_msg(descr)}.axes[{a.id}].size.axis_id: "
                        f"Unknown tensor axis reference '{a.size.tensor_id}.{a.size.axis_id}"
                    )

                if a.unit != ref_axis.unit:
                    raise ValueError(
                        f"{e_msg(descr)}.axes[{a.id}].size: `SizeReference` requires axis and reference axis to have "
                        f"the same `unit`, but {a.unit}!={ref_axis.unit}"
                    )

                if actual_size != (expected_size := (ref_size * ref_axis.scale / a.scale + a.size.offset)):
                    raise ValueError(
                        f"{e_msg(descr)}.{tensor_origin}: axis '{a.id}' of size {actual_size} invalid "
                        f"for referenced size {ref_size}; expected {expected_size}"
                    )
            else:
                assert_never(a.size)


class EnvironmentFileDescr(FileDescr):
    source: Annotated[
        ImportantFileSource,
        WithSuffix((".yaml", ".yml"), case_sensitive=True),
        Field(
            examples=["environment.yaml"],
        ),
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


class _ArchFileConv(Converter[v0_4.CallableFromFile, ArchitectureFromFileDescr, Optional[Sha256], Dict[str, Any]]):
    def _convert(
        self,
        src: v0_4.CallableFromFile,
        tgt: "type[ArchitectureFromFileDescr | dict[str, Any]]",
        sha256: Optional[Sha256],
        kwargs: Dict[str, Any],
    ) -> "ArchitectureFromFileDescr | dict[str, Any]":
        if src.startswith("http") and src.count(":") == 2:
            http, source, callable_ = src.split(":")
            source = ":".join((http, source))
        elif not src.startswith("http") and src.count(":") == 1:
            source, callable_ = src.split(":")
        else:
            source = str(src)
            callable_ = str(src)
        return tgt(
            callable=Identifier(callable_), source=cast(ImportantFileSource, source), sha256=sha256, kwargs=kwargs
        )


_arch_file_conv = _ArchFileConv(v0_4.CallableFromFile, ArchitectureFromFileDescr)


class _ArchLibConv(Converter[v0_4.CallableFromDepencency, ArchitectureFromLibraryDescr, Dict[str, Any]]):
    def _convert(
        self,
        src: v0_4.CallableFromDepencency,
        tgt: "type[ArchitectureFromLibraryDescr | dict[str, Any]]",
        kwargs: Dict[str, Any],
    ) -> "ArchitectureFromLibraryDescr | dict[str, Any]":
        *mods, callable_ = src.split(".")
        import_from = ".".join(mods)
        return tgt(import_from=import_from, callable=Identifier(callable_), kwargs=kwargs)


_arch_lib_conv = _ArchLibConv(v0_4.CallableFromDepencency, ArchitectureFromLibraryDescr)


class WeightsEntryDescrBase(FileDescr):
    type: ClassVar[WeightsFormat]
    weights_format_name: ClassVar[str]  # human readable

    source: ImportantFileSource
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
    tensorflow_version: _Version
    """TensorFlow version used to create these weights."""


class OnnxWeightsDescr(WeightsEntryDescrBase):
    type = "onnx"
    weights_format_name: ClassVar[str] = "ONNX"
    opset_version: Annotated[int, Ge(7)]
    """ONNX opset version"""


class PytorchStateDictWeightsDescr(WeightsEntryDescrBase):
    type = "pytorch_state_dict"
    weights_format_name: ClassVar[str] = "Pytorch State Dict"
    architecture: ArchitectureDescr
    pytorch_version: _Version
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
    tensorflow_version: _Version
    """Version of the TensorFlow library used."""

    source: ImportantFileSource
    """∈📦 The multi-file weights.
    All required files/folders should be a zip archive."""


class TensorflowSavedModelBundleWeightsDescr(WeightsEntryDescrBase):
    type = "tensorflow_saved_model_bundle"
    weights_format_name: ClassVar[str] = "Tensorflow Saved Model"
    tensorflow_version: _Version
    """Version of the TensorFlow library used."""

    dependencies: Optional[EnvironmentFileDescr] = None
    """Custom dependencies beyond tensorflow.
    Should include tensorflow and any version pinning has to be compatible with `tensorflow_version`."""

    source: ImportantFileSource
    """∈📦 The multi-file weights.
    All required files/folders should be a zip archive."""


class TorchscriptWeightsDescr(WeightsEntryDescrBase):
    type = "torchscript"
    weights_format_name: ClassVar[str] = "TorchScript"
    pytorch_version: _Version
    """Version of the PyTorch library used."""


class WeightsDescr(Node):
    keras_hdf5: Optional[KerasHdf5WeightsDescr] = None
    onnx: Optional[OnnxWeightsDescr] = None
    pytorch_state_dict: Optional[PytorchStateDictWeightsDescr] = None
    tensorflow_js: Optional[TensorflowJsWeightsDescr] = None
    tensorflow_saved_model_bundle: Optional[TensorflowSavedModelBundleWeightsDescr] = None
    torchscript: Optional[TorchscriptWeightsDescr] = None

    @model_validator(mode="after")
    def check_entries(self) -> Self:
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
        DocumentationSource,
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
    def _validate_input_axes(cls, inputs: Sequence[InputTensorDescr]) -> Sequence[InputTensorDescr]:
        input_size_refs = cls._get_axes_with_independent_size(inputs)

        for i, ipt in enumerate(inputs):
            valid_independent_refs: Dict[
                Tuple[TensorId, AxisId], Tuple[TensorDescr, AnyAxis, Union[int, ParameterizedSize]]
            ] = {
                **{
                    (ipt.id, a.id): (ipt, a, a.size)
                    for a in ipt.axes
                    if not isinstance(a, BatchAxis) and isinstance(a.size, (int, ParameterizedSize))
                },
                **input_size_refs,
            }
            for a, ax in enumerate(ipt.axes):
                cls._validate_axis(
                    "inputs",
                    i=i,
                    tensor_id=ipt.id,
                    a=a,
                    axis=ax,
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
            Tuple[TensorId, AxisId], Tuple[TensorDescr, AnyAxis, Union[int, ParameterizedSize]]
        ],
    ):
        if isinstance(axis, BatchAxis) or isinstance(axis.size, int):
            return

        if isinstance(axis.size, ParameterizedSize):
            if isinstance(axis, WithHalo) and (axis.size.min - 2 * axis.halo) < 1:
                raise ValueError(f"axis {axis.id} with minimum size {axis.size.min} is too small for halo {axis.halo}.")

        elif isinstance(axis.size, SizeReference):
            ref = (axis.size.tensor_id, axis.size.axis_id)
            if ref not in valid_independent_refs:
                raise ValueError(f"Invalid tensor axis reference at {field_name}[{i}].axes[{a}].size: {axis.size}.")
            if ref == (tensor_id, axis.id):
                raise ValueError(f"Self-referencing not allowed for {field_name}[{i}].axes[{a}].size: {axis.size}")
            if axis.type == "channel":
                if valid_independent_refs[ref][1].type != "channel":
                    raise ValueError("A channel axis' size may only reference another fixed size channel axis.")
                if isinstance(axis.channel_names, str) and "{i}" in axis.channel_names:
                    ref_size = valid_independent_refs[ref][2]
                    assert isinstance(
                        ref_size, int
                    ), "channel axis ref (another channel axis) has to specify fixed size"
                    generated_channel_names = [
                        Identifier(axis.channel_names.format(i=i)) for i in range(1, ref_size + 1)
                    ]
                    axis.channel_names = generated_channel_names

            if (ax_unit := getattr(axis, "unit", None)) != (
                ref_unit := getattr(valid_independent_refs[ref][1], "unit", None)
            ):
                raise ValueError(
                    f"The units of an axis and its reference axis need to match, but '{ax_unit}' != '{ref_unit}'."
                )
            min_size = valid_independent_refs[ref][2]
            if isinstance(min_size, ParameterizedSize):
                min_size = min_size.min

            if isinstance(axis, WithHalo) and (min_size - 2 * axis.halo) < 1:
                raise ValueError(f"axis {axis.id} with minimum size {min_size} is too small for halo {axis.halo}.")

        else:
            assert_never(axis.size)

    @model_validator(mode="after")
    def _validate_test_tensors(self) -> Self:
        if not validation_context_var.get().perform_io_checks:
            return self

        test_arrays = [load_array(descr.test_tensor.download().path) for descr in chain(self.inputs, self.outputs)]
        tensors = {descr.id: (descr, array) for descr, array in zip(chain(self.inputs, self.outputs), test_arrays)}
        validate_tensors(tensors, tensor_origin="test_tensor")
        return self

    @model_validator(mode="after")
    def _validate_tensor_references_in_proc_kwargs(self, info: ValidationInfo) -> Self:
        ipt_refs = {t.id for t in self.inputs}
        out_refs = {t.id for t in self.outputs}
        for ipt in self.inputs:
            for p in ipt.preprocessing:
                ref = p.kwargs.get("reference_tensor")
                if ref is None:
                    continue
                if ref not in ipt_refs:
                    raise ValueError(
                        f"`reference_tensor` '{ref}' not found. Valid input tensor references are: {ipt_refs}."
                    )

        for out in self.outputs:
            for p in out.postprocessing:
                ref = p.kwargs.get("reference_tensor")
                if ref is None:
                    continue

                if ref not in ipt_refs and ref not in out_refs:
                    raise ValueError(
                        f"`reference_tensor` '{ref}' not found. Valid tensor references are: {ipt_refs | out_refs}."
                    )

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

    outputs: NotEmpty[Sequence[OutputTensorDescr]]
    """Describes the output tensors."""

    @field_validator("outputs", mode="after")
    @classmethod
    def _validate_tensor_ids(
        cls, outputs: Sequence[OutputTensorDescr], info: ValidationInfo
    ) -> Sequence[OutputTensorDescr]:
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
            (t.id, a.id): (t, a, a.size)
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis) and isinstance(a.size, (int, ParameterizedSize))
        }

    @field_validator("outputs", mode="after")
    @classmethod
    def _validate_output_axes(cls, outputs: List[OutputTensorDescr], info: ValidationInfo) -> List[OutputTensorDescr]:
        input_size_refs = cls._get_axes_with_independent_size(info.data.get("inputs", []))
        output_size_refs = cls._get_axes_with_independent_size(outputs)

        for i, out in enumerate(outputs):
            valid_independent_refs: Dict[
                Tuple[TensorId, AxisId], Tuple[TensorDescr, AnyAxis, Union[int, ParameterizedSize]]
            ] = {
                **{
                    (out.id, a.id): (out, a, a.size)
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
    def _add_default_cover(self) -> Self:
        if not validation_context_var.get().perform_io_checks or self.covers:
            return self

        try:
            from bioimageio.spec._internal.cover import generate_covers  # TODO: move import?

            generated_covers = generate_covers(
                [(t, load_array(t.test_tensor.download().path)) for t in self.inputs],
                [(t, load_array(t.test_tensor.download().path)) for t in self.outputs],
            )
        except Exception as e:
            issue_warning(
                "Failed to generate cover image(s): {e}",
                value=self.covers,
                msg_context=dict(e=e),
            )
        else:
            self.covers.extend(generated_covers)

        return self

    def get_input_test_arrays(self) -> List[NDArray[Any]]:
        data = [load_array(ipt.test_tensor.download().path) for ipt in self.inputs]
        assert all(isinstance(d, np.ndarray) for d in data)
        return data

    def get_output_test_arrays(self) -> List[NDArray[Any]]:
        data = [load_array(out.test_tensor.download().path) for out in self.outputs]
        assert all(isinstance(d, np.ndarray) for d in data)
        return data

    @model_validator(mode="before")
    @classmethod
    def _convert(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if (
            data.get("type") == "model"
            and isinstance(fv := data.get("format_version"), str)
            and (fv.startswith("0.3.") or fv.startswith("0.4."))
        ):
            m04 = v0_4.ModelDescr.load(data)
            if not isinstance(m04, InvalidDescription):
                return _model_conv.convert_as_dict(m04)

        return data


class _ModelConv(Converter[v0_4.ModelDescr, ModelDescr]):
    def _convert(
        self, src: v0_4.ModelDescr, tgt: "type[ModelDescr] | type[dict[str, Any]]"
    ) -> "ModelDescr | dict[str, Any]":
        def conv_authors(auths: Optional[Sequence[v0_4.Author]]):
            conv = _author_conv.convert if TYPE_CHECKING else _author_conv.convert_as_dict
            return None if auths is None else [conv(a) for a in auths]

        if TYPE_CHECKING:
            arch_file_conv = _arch_file_conv.convert
            arch_lib_conv = _arch_lib_conv.convert
        else:
            arch_file_conv = _arch_file_conv.convert_as_dict
            arch_lib_conv = _arch_lib_conv.convert_as_dict

        return tgt(
            attachments=[] if src.attachments is None else [FileDescr(source=f) for f in src.attachments.files],
            authors=[_author_conv.convert_as_dict(a) for a in src.authors],  # pyright: ignore[reportArgumentType]
            cite=src.cite,
            config=src.config,
            covers=src.covers,
            description=src.description,
            documentation=src.documentation,
            format_version="0.5.0",
            git_repo=cast(Optional[HttpUrl], src.git_repo),
            icon=src.icon,
            id=src.id,
            id_emoji=src.id_emoji,
            license=src.license,  # type: ignore
            links=src.links,
            maintainers=[
                _maintainer_conv.convert_as_dict(m) for m in src.maintainers
            ],  # pyright: ignore[reportArgumentType]
            name=src.name,
            tags=src.tags,
            type=src.type,
            version=src.version,
            inputs=[  # pyright: ignore[reportArgumentType]
                _input_tensor_conv.convert_as_dict(ipt, tt, st)
                for ipt, tt, st, in zip(src.inputs, src.test_inputs, src.sample_inputs or [None] * len(src.test_inputs))
            ],
            outputs=[  # pyright: ignore[reportArgumentType]
                _output_tensor_conv.convert_as_dict(out, tt, st)
                for out, tt, st, in zip(
                    src.outputs, src.test_outputs, src.sample_outputs or [None] * len(src.test_outputs)
                )
            ],
            weights=(WeightsDescr if TYPE_CHECKING else dict)(
                keras_hdf5=(w := src.weights.keras_hdf5)
                and (KerasHdf5WeightsDescr if TYPE_CHECKING else dict)(
                    authors=conv_authors(w.authors),
                    source=w.source,
                    tensorflow_version=w.tensorflow_version or Version("1.15"),
                    parent=w.parent,
                ),
                onnx=(w := src.weights.onnx)
                and (OnnxWeightsDescr if TYPE_CHECKING else dict)(
                    source=w.source,
                    authors=conv_authors(w.authors),
                    parent=w.parent,
                    opset_version=w.opset_version or 15,
                ),
                pytorch_state_dict=(w := src.weights.pytorch_state_dict)
                and (PytorchStateDictWeightsDescr if TYPE_CHECKING else dict)(
                    source=w.source,
                    authors=conv_authors(w.authors),
                    parent=w.parent,
                    architecture=arch_file_conv(
                        w.architecture,
                        w.architecture_sha256,
                        w.kwargs,
                    )
                    if isinstance(w.architecture, v0_4.CallableFromFile)
                    else arch_lib_conv(w.architecture, w.kwargs),
                    pytorch_version=w.pytorch_version or Version("1.10"),
                    dependencies=None
                    if w.dependencies is None
                    else (EnvironmentFileDescr if TYPE_CHECKING else dict)(
                        source=cast(
                            ImportantFileSource,
                            str(deps := w.dependencies)[len("conda:") if str(deps).startswith("conda:") else 0 :],
                        )
                    ),
                ),
                tensorflow_js=(w := src.weights.tensorflow_js)
                and (TensorflowJsWeightsDescr if TYPE_CHECKING else dict)(
                    source=w.source,
                    authors=conv_authors(w.authors),
                    parent=w.parent,
                    tensorflow_version=w.tensorflow_version or Version("1.15"),
                ),
                tensorflow_saved_model_bundle=(w := src.weights.tensorflow_saved_model_bundle)
                and (TensorflowSavedModelBundleWeightsDescr if TYPE_CHECKING else dict)(
                    authors=conv_authors(w.authors),
                    parent=w.parent,
                    source=w.source,
                    tensorflow_version=w.tensorflow_version or Version("1.15"),
                    dependencies=None
                    if w.dependencies is None
                    else (EnvironmentFileDescr if TYPE_CHECKING else dict)(
                        source=cast(
                            ImportantFileSource,
                            str(w.dependencies)[len("conda:") :]
                            if str(w.dependencies).startswith("conda:")
                            else str(w.dependencies),
                        )
                    ),
                ),
                torchscript=(w := src.weights.torchscript)
                and (TorchscriptWeightsDescr if TYPE_CHECKING else dict)(
                    source=w.source,
                    authors=conv_authors(w.authors),
                    parent=w.parent,
                    pytorch_version=w.pytorch_version or Version("1.10"),
                ),
            ),
        )


_model_conv = _ModelConv(v0_4.ModelDescr, ModelDescr)
