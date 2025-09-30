from __future__ import annotations

import collections.abc
import re
import string
import warnings
from abc import ABC
from copy import deepcopy
from itertools import chain
from math import ceil
from pathlib import Path, PurePosixPath
from tempfile import mkdtemp
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    List,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import numpy as np
from annotated_types import Ge, Gt, Interval, MaxLen, MinLen, Predicate
from imageio.v3 import imread, imwrite  # pyright: ignore[reportUnknownVariableType]
from loguru import logger
from numpy.typing import NDArray
from pydantic import (
    AfterValidator,
    Discriminator,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    StrictInt,
    Tag,
    ValidationInfo,
    WrapSerializer,
    field_validator,
    model_serializer,
    model_validator,
)
from typing_extensions import Annotated, Self, assert_never, get_args

from .._internal.common_nodes import (
    InvalidDescr,
    Node,
    NodeWithExplicitlySetFields,
)
from .._internal.constants import DTYPE_LIMITS
from .._internal.field_warning import issue_warning, warn
from .._internal.io import BioimageioYamlContent as BioimageioYamlContent
from .._internal.io import FileDescr as FileDescr
from .._internal.io import (
    FileSource,
    WithSuffix,
    YamlValue,
    get_reader,
    wo_special_file_name,
)
from .._internal.io_basics import Sha256 as Sha256
from .._internal.io_packaging import (
    FileDescr_,
    FileSource_,
    package_file_descr_serializer,
)
from .._internal.io_utils import load_array
from .._internal.node_converter import Converter
from .._internal.type_guards import is_dict, is_sequence
from .._internal.types import (
    FAIR,
    AbsoluteTolerance,
    LowerCaseIdentifier,
    LowerCaseIdentifierAnno,
    MismatchedElementsPerMillion,
    RelativeTolerance,
)
from .._internal.types import Datetime as Datetime
from .._internal.types import Identifier as Identifier
from .._internal.types import NotEmpty as NotEmpty
from .._internal.types import SiUnit as SiUnit
from .._internal.url import HttpUrl as HttpUrl
from .._internal.validation_context import get_validation_context
from .._internal.validator_annotations import RestrictCharacters
from .._internal.version_type import Version as Version
from .._internal.warning_levels import INFO
from ..dataset.v0_2 import DatasetDescr as DatasetDescr02
from ..dataset.v0_2 import LinkedDataset as LinkedDataset02
from ..dataset.v0_3 import DatasetDescr as DatasetDescr
from ..dataset.v0_3 import DatasetId as DatasetId
from ..dataset.v0_3 import LinkedDataset as LinkedDataset
from ..dataset.v0_3 import Uploader as Uploader
from ..generic.v0_3 import (
    VALID_COVER_IMAGE_EXTENSIONS as VALID_COVER_IMAGE_EXTENSIONS,
)
from ..generic.v0_3 import Author as Author
from ..generic.v0_3 import BadgeDescr as BadgeDescr
from ..generic.v0_3 import CiteEntry as CiteEntry
from ..generic.v0_3 import DeprecatedLicenseId as DeprecatedLicenseId
from ..generic.v0_3 import Doi as Doi
from ..generic.v0_3 import (
    FileSource_documentation,
    GenericModelDescrBase,
    LinkedResourceBase,
    _author_conv,  # pyright: ignore[reportPrivateUsage]
    _maintainer_conv,  # pyright: ignore[reportPrivateUsage]
)
from ..generic.v0_3 import LicenseId as LicenseId
from ..generic.v0_3 import LinkedResource as LinkedResource
from ..generic.v0_3 import Maintainer as Maintainer
from ..generic.v0_3 import OrcidId as OrcidId
from ..generic.v0_3 import RelativeFilePath as RelativeFilePath
from ..generic.v0_3 import ResourceId as ResourceId
from .v0_4 import Author as _Author_v0_4
from .v0_4 import BinarizeDescr as _BinarizeDescr_v0_4
from .v0_4 import CallableFromDepencency as CallableFromDepencency
from .v0_4 import CallableFromDepencency as _CallableFromDepencency_v0_4
from .v0_4 import CallableFromFile as _CallableFromFile_v0_4
from .v0_4 import ClipDescr as _ClipDescr_v0_4
from .v0_4 import ClipKwargs as ClipKwargs
from .v0_4 import ImplicitOutputShape as _ImplicitOutputShape_v0_4
from .v0_4 import InputTensorDescr as _InputTensorDescr_v0_4
from .v0_4 import KnownRunMode as KnownRunMode
from .v0_4 import ModelDescr as _ModelDescr_v0_4
from .v0_4 import OutputTensorDescr as _OutputTensorDescr_v0_4
from .v0_4 import ParameterizedInputShape as _ParameterizedInputShape_v0_4
from .v0_4 import PostprocessingDescr as _PostprocessingDescr_v0_4
from .v0_4 import PreprocessingDescr as _PreprocessingDescr_v0_4
from .v0_4 import ProcessingKwargs as ProcessingKwargs
from .v0_4 import RunMode as RunMode
from .v0_4 import ScaleLinearDescr as _ScaleLinearDescr_v0_4
from .v0_4 import ScaleMeanVarianceDescr as _ScaleMeanVarianceDescr_v0_4
from .v0_4 import ScaleRangeDescr as _ScaleRangeDescr_v0_4
from .v0_4 import SigmoidDescr as _SigmoidDescr_v0_4
from .v0_4 import TensorName as _TensorName_v0_4
from .v0_4 import WeightsFormat as WeightsFormat
from .v0_4 import ZeroMeanUnitVarianceDescr as _ZeroMeanUnitVarianceDescr_v0_4
from .v0_4 import package_weights

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
"""Space unit compatible to the [OME-Zarr axes specification 0.5](https://ngff.openmicroscopy.org/0.5/#axes-md)"""

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
"""Time unit compatible to the [OME-Zarr axes specification 0.5](https://ngff.openmicroscopy.org/0.5/#axes-md)"""

AxisType = Literal["batch", "channel", "index", "time", "space"]

_AXIS_TYPE_MAP: Mapping[str, AxisType] = {
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


class TensorId(LowerCaseIdentifier):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
        Annotated[LowerCaseIdentifierAnno, MaxLen(32)]
    ]


def _normalize_axis_id(a: str):
    a = str(a)
    normalized = _AXIS_ID_MAP.get(a, a)
    if a != normalized:
        logger.opt(depth=3).warning(
            "Normalized axis id from '{}' to '{}'.", a, normalized
        )
    return normalized


class AxisId(LowerCaseIdentifier):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
        Annotated[
            LowerCaseIdentifierAnno,
            MaxLen(16),
            AfterValidator(_normalize_axis_id),
        ]
    ]


def _is_batch(a: str) -> bool:
    return str(a) == "batch"


def _is_not_batch(a: str) -> bool:
    return not _is_batch(a)


NonBatchAxisId = Annotated[AxisId, Predicate(_is_not_batch)]

PreprocessingId = Literal[
    "binarize",
    "clip",
    "ensure_dtype",
    "fixed_zero_mean_unit_variance",
    "scale_linear",
    "scale_range",
    "sigmoid",
    "softmax",
]
PostprocessingId = Literal[
    "binarize",
    "clip",
    "ensure_dtype",
    "fixed_zero_mean_unit_variance",
    "scale_linear",
    "scale_mean_variance",
    "scale_range",
    "sigmoid",
    "softmax",
    "zero_mean_unit_variance",
]


SAME_AS_TYPE = "<same as type>"


ParameterizedSize_N = int
"""
Annotates an integer to calculate a concrete axis size from a `ParameterizedSize`.
"""


class ParameterizedSize(Node):
    """Describes a range of valid tensor axis sizes as `size = min + n*step`.

    - **min** and **step** are given by the model description.
    - All blocksize paramters n = 0,1,2,... yield a valid `size`.
    - A greater blocksize paramter n = 0,1,2,... results in a greater **size**.
      This allows to adjust the axis size more generically.
    """

    N: ClassVar[Type[int]] = ParameterizedSize_N
    """Positive integer to parameterize this axis"""

    min: Annotated[int, Gt(0)]
    step: Annotated[int, Gt(0)]

    def validate_size(self, size: int) -> int:
        if size < self.min:
            raise ValueError(f"size {size} < {self.min}")
        if (size - self.min) % self.step != 0:
            raise ValueError(
                f"axis of size {size} is not parameterized by `min + n*step` ="
                + f" `{self.min} + n*{self.step}`"
            )

        return size

    def get_size(self, n: ParameterizedSize_N) -> int:
        return self.min + self.step * n

    def get_n(self, s: int) -> ParameterizedSize_N:
        """return smallest n parameterizing a size greater or equal than `s`"""
        return ceil((s - self.min) / self.step)


class DataDependentSize(Node):
    min: Annotated[int, Gt(0)] = 1
    max: Annotated[Optional[int], Gt(1)] = None

    @model_validator(mode="after")
    def _validate_max_gt_min(self):
        if self.max is not None and self.min >= self.max:
            raise ValueError(f"expected `min` < `max`, but got {self.min}, {self.max}")

        return self

    def validate_size(self, size: int) -> int:
        if size < self.min:
            raise ValueError(f"size {size} < {self.min}")

        if self.max is not None and size > self.max:
            raise ValueError(f"size {size} > {self.max}")

        return size


class SizeReference(Node):
    """A tensor axis size (extent in pixels/frames) defined in relation to a reference axis.

    `axis.size = reference.size * reference.scale / axis.scale + offset`

    Note:
    1. The axis and the referenced axis need to have the same unit (or no unit).
    2. Batch axes may not be referenced.
    3. Fractions are rounded down.
    4. If the reference axis is `concatenable` the referencing axis is assumed to be
        `concatenable` as well with the same block order.

    Example:
    An unisotropic input image of w*h=100*49 pixels depicts a phsical space of 200*196mm².
    Let's assume that we want to express the image height h in relation to its width w
    instead of only accepting input images of exactly 100*49 pixels
    (for example to express a range of valid image shapes by parametrizing w, see `ParameterizedSize`).

    >>> w = SpaceInputAxis(id=AxisId("w"), size=100, unit="millimeter", scale=2)
    >>> h = SpaceInputAxis(
    ...     id=AxisId("h"),
    ...     size=SizeReference(tensor_id=TensorId("input"), axis_id=AxisId("w"), offset=-1),
    ...     unit="millimeter",
    ...     scale=4,
    ... )
    >>> print(h.size.get_size(h, w))
    49

    ⇒ h = w * w.scale / h.scale + offset = 100 * 2mm / 4mm - 1 = 49
    """

    tensor_id: TensorId
    """tensor id of the reference axis"""

    axis_id: AxisId
    """axis id of the reference axis"""

    offset: StrictInt = 0

    def get_size(
        self,
        axis: Union[
            ChannelAxis,
            IndexInputAxis,
            IndexOutputAxis,
            TimeInputAxis,
            SpaceInputAxis,
            TimeOutputAxis,
            TimeOutputAxisWithHalo,
            SpaceOutputAxis,
            SpaceOutputAxisWithHalo,
        ],
        ref_axis: Union[
            ChannelAxis,
            IndexInputAxis,
            IndexOutputAxis,
            TimeInputAxis,
            SpaceInputAxis,
            TimeOutputAxis,
            TimeOutputAxisWithHalo,
            SpaceOutputAxis,
            SpaceOutputAxisWithHalo,
        ],
        n: ParameterizedSize_N = 0,
        ref_size: Optional[int] = None,
    ):
        """Compute the concrete size for a given axis and its reference axis.

        Args:
            axis: The axis this `SizeReference` is the size of.
            ref_axis: The reference axis to compute the size from.
            n: If the **ref_axis** is parameterized (of type `ParameterizedSize`)
                and no fixed **ref_size** is given,
                **n** is used to compute the size of the parameterized **ref_axis**.
            ref_size: Overwrite the reference size instead of deriving it from
                **ref_axis**
                (**ref_axis.scale** is still used; any given **n** is ignored).
        """
        assert axis.size == self, (
            "Given `axis.size` is not defined by this `SizeReference`"
        )

        assert ref_axis.id == self.axis_id, (
            f"Expected `ref_axis.id` to be {self.axis_id}, but got {ref_axis.id}."
        )

        assert axis.unit == ref_axis.unit, (
            "`SizeReference` requires `axis` and `ref_axis` to have the same `unit`,"
            f" but {axis.unit}!={ref_axis.unit}"
        )
        if ref_size is None:
            if isinstance(ref_axis.size, (int, float)):
                ref_size = ref_axis.size
            elif isinstance(ref_axis.size, ParameterizedSize):
                ref_size = ref_axis.size.get_size(n)
            elif isinstance(ref_axis.size, DataDependentSize):
                raise ValueError(
                    "Reference axis referenced in `SizeReference` may not be a `DataDependentSize`."
                )
            elif isinstance(ref_axis.size, SizeReference):
                raise ValueError(
                    "Reference axis referenced in `SizeReference` may not be sized by a"
                    + " `SizeReference` itself."
                )
            else:
                assert_never(ref_axis.size)

        return int(ref_size * ref_axis.scale / axis.scale + self.offset)

    @staticmethod
    def _get_unit(
        axis: Union[
            ChannelAxis,
            IndexInputAxis,
            IndexOutputAxis,
            TimeInputAxis,
            SpaceInputAxis,
            TimeOutputAxis,
            TimeOutputAxisWithHalo,
            SpaceOutputAxis,
            SpaceOutputAxisWithHalo,
        ],
    ):
        return axis.unit


class AxisBase(NodeWithExplicitlySetFields):
    id: AxisId
    """An axis id unique across all axes of one tensor."""

    description: Annotated[str, MaxLen(128)] = ""
    """A short description of this axis beyond its type and id."""


class WithHalo(Node):
    halo: Annotated[int, Ge(1)]
    """The halo should be cropped from the output tensor to avoid boundary effects.
    It is to be cropped from both sides, i.e. `size_after_crop = size - 2 * halo`.
    To document a halo that is already cropped by the model use `size.offset` instead."""

    size: Annotated[
        SizeReference,
        Field(
            examples=[
                10,
                SizeReference(
                    tensor_id=TensorId("t"), axis_id=AxisId("a"), offset=5
                ).model_dump(mode="json"),
            ]
        ),
    ]
    """reference to another axis with an optional offset (see `SizeReference`)"""


BATCH_AXIS_ID = AxisId("batch")


class BatchAxis(AxisBase):
    implemented_type: ClassVar[Literal["batch"]] = "batch"
    if TYPE_CHECKING:
        type: Literal["batch"] = "batch"
    else:
        type: Literal["batch"]

    id: Annotated[AxisId, Predicate(_is_batch)] = BATCH_AXIS_ID
    size: Optional[Literal[1]] = None
    """The batch size may be fixed to 1,
    otherwise (the default) it may be chosen arbitrarily depending on available memory"""

    @property
    def scale(self):
        return 1.0

    @property
    def concatenable(self):
        return True

    @property
    def unit(self):
        return None


class ChannelAxis(AxisBase):
    implemented_type: ClassVar[Literal["channel"]] = "channel"
    if TYPE_CHECKING:
        type: Literal["channel"] = "channel"
    else:
        type: Literal["channel"]

    id: NonBatchAxisId = AxisId("channel")

    channel_names: NotEmpty[List[Identifier]]

    @property
    def size(self) -> int:
        return len(self.channel_names)

    @property
    def concatenable(self):
        return False

    @property
    def scale(self) -> float:
        return 1.0

    @property
    def unit(self):
        return None


class IndexAxisBase(AxisBase):
    implemented_type: ClassVar[Literal["index"]] = "index"
    if TYPE_CHECKING:
        type: Literal["index"] = "index"
    else:
        type: Literal["index"]

    id: NonBatchAxisId = AxisId("index")

    @property
    def scale(self) -> float:
        return 1.0

    @property
    def unit(self):
        return None


class _WithInputAxisSize(Node):
    size: Annotated[
        Union[Annotated[int, Gt(0)], ParameterizedSize, SizeReference],
        Field(
            examples=[
                10,
                ParameterizedSize(min=32, step=16).model_dump(mode="json"),
                SizeReference(
                    tensor_id=TensorId("t"), axis_id=AxisId("a"), offset=5
                ).model_dump(mode="json"),
            ]
        ),
    ]
    """The size/length of this axis can be specified as
    - fixed integer
    - parameterized series of valid sizes (`ParameterizedSize`)
    - reference to another axis with an optional offset (`SizeReference`)
    """


class IndexInputAxis(IndexAxisBase, _WithInputAxisSize):
    concatenable: bool = False
    """If a model has a `concatenable` input axis, it can be processed blockwise,
    splitting a longer sample axis into blocks matching its input tensor description.
    Output axes are concatenable if they have a `SizeReference` to a concatenable
    input axis.
    """


class IndexOutputAxis(IndexAxisBase):
    size: Annotated[
        Union[Annotated[int, Gt(0)], SizeReference, DataDependentSize],
        Field(
            examples=[
                10,
                SizeReference(
                    tensor_id=TensorId("t"), axis_id=AxisId("a"), offset=5
                ).model_dump(mode="json"),
            ]
        ),
    ]
    """The size/length of this axis can be specified as
    - fixed integer
    - reference to another axis with an optional offset (`SizeReference`)
    - data dependent size using `DataDependentSize` (size is only known after model inference)
    """


class TimeAxisBase(AxisBase):
    implemented_type: ClassVar[Literal["time"]] = "time"
    if TYPE_CHECKING:
        type: Literal["time"] = "time"
    else:
        type: Literal["time"]

    id: NonBatchAxisId = AxisId("time")
    unit: Optional[TimeUnit] = None
    scale: Annotated[float, Gt(0)] = 1.0


class TimeInputAxis(TimeAxisBase, _WithInputAxisSize):
    concatenable: bool = False
    """If a model has a `concatenable` input axis, it can be processed blockwise,
    splitting a longer sample axis into blocks matching its input tensor description.
    Output axes are concatenable if they have a `SizeReference` to a concatenable
    input axis.
    """


class SpaceAxisBase(AxisBase):
    implemented_type: ClassVar[Literal["space"]] = "space"
    if TYPE_CHECKING:
        type: Literal["space"] = "space"
    else:
        type: Literal["space"]

    id: Annotated[NonBatchAxisId, Field(examples=["x", "y", "z"])] = AxisId("x")
    unit: Optional[SpaceUnit] = None
    scale: Annotated[float, Gt(0)] = 1.0


class SpaceInputAxis(SpaceAxisBase, _WithInputAxisSize):
    concatenable: bool = False
    """If a model has a `concatenable` input axis, it can be processed blockwise,
    splitting a longer sample axis into blocks matching its input tensor description.
    Output axes are concatenable if they have a `SizeReference` to a concatenable
    input axis.
    """


INPUT_AXIS_TYPES = (
    BatchAxis,
    ChannelAxis,
    IndexInputAxis,
    TimeInputAxis,
    SpaceInputAxis,
)
"""intended for isinstance comparisons in py<3.10"""

_InputAxisUnion = Union[
    BatchAxis, ChannelAxis, IndexInputAxis, TimeInputAxis, SpaceInputAxis
]
InputAxis = Annotated[_InputAxisUnion, Discriminator("type")]


class _WithOutputAxisSize(Node):
    size: Annotated[
        Union[Annotated[int, Gt(0)], SizeReference],
        Field(
            examples=[
                10,
                SizeReference(
                    tensor_id=TensorId("t"), axis_id=AxisId("a"), offset=5
                ).model_dump(mode="json"),
            ]
        ),
    ]
    """The size/length of this axis can be specified as
    - fixed integer
    - reference to another axis with an optional offset (see `SizeReference`)
    """


class TimeOutputAxis(TimeAxisBase, _WithOutputAxisSize):
    pass


class TimeOutputAxisWithHalo(TimeAxisBase, WithHalo):
    pass


def _get_halo_axis_discriminator_value(v: Any) -> Literal["with_halo", "wo_halo"]:
    if isinstance(v, dict):
        return "with_halo" if "halo" in v else "wo_halo"
    else:
        return "with_halo" if hasattr(v, "halo") else "wo_halo"


_TimeOutputAxisUnion = Annotated[
    Union[
        Annotated[TimeOutputAxis, Tag("wo_halo")],
        Annotated[TimeOutputAxisWithHalo, Tag("with_halo")],
    ],
    Discriminator(_get_halo_axis_discriminator_value),
]


class SpaceOutputAxis(SpaceAxisBase, _WithOutputAxisSize):
    pass


class SpaceOutputAxisWithHalo(SpaceAxisBase, WithHalo):
    pass


_SpaceOutputAxisUnion = Annotated[
    Union[
        Annotated[SpaceOutputAxis, Tag("wo_halo")],
        Annotated[SpaceOutputAxisWithHalo, Tag("with_halo")],
    ],
    Discriminator(_get_halo_axis_discriminator_value),
]


_OutputAxisUnion = Union[
    BatchAxis, ChannelAxis, IndexOutputAxis, _TimeOutputAxisUnion, _SpaceOutputAxisUnion
]
OutputAxis = Annotated[_OutputAxisUnion, Discriminator("type")]

OUTPUT_AXIS_TYPES = (
    BatchAxis,
    ChannelAxis,
    IndexOutputAxis,
    TimeOutputAxis,
    TimeOutputAxisWithHalo,
    SpaceOutputAxis,
    SpaceOutputAxisWithHalo,
)
"""intended for isinstance comparisons in py<3.10"""


AnyAxis = Union[InputAxis, OutputAxis]

ANY_AXIS_TYPES = INPUT_AXIS_TYPES + OUTPUT_AXIS_TYPES
"""intended for isinstance comparisons in py<3.10"""

TVs = Union[
    NotEmpty[List[int]],
    NotEmpty[List[float]],
    NotEmpty[List[bool]],
    NotEmpty[List[str]],
]


NominalOrOrdinalDType = Literal[
    "float32",
    "float64",
    "uint8",
    "int8",
    "uint16",
    "int16",
    "uint32",
    "int32",
    "uint64",
    "int64",
    "bool",
]


class NominalOrOrdinalDataDescr(Node):
    values: TVs
    """A fixed set of nominal or an ascending sequence of ordinal values.
    In this case `data.type` is required to be an unsigend integer type, e.g. 'uint8'.
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
    def _validate_values_match_type(
        self,
    ) -> Self:
        incompatible: List[Any] = []
        for v in self.values:
            if self.type == "bool":
                if not isinstance(v, bool):
                    incompatible.append(v)
            elif self.type in DTYPE_LIMITS:
                if (
                    isinstance(v, (int, float))
                    and (
                        v < DTYPE_LIMITS[self.type].min
                        or v > DTYPE_LIMITS[self.type].max
                    )
                    or (isinstance(v, str) and "uint" not in self.type)
                    or (isinstance(v, float) and "int" in self.type)
                ):
                    incompatible.append(v)
            else:
                incompatible.append(v)

            if len(incompatible) == 5:
                incompatible.append("...")
                break

        if incompatible:
            raise ValueError(
                f"data type '{self.type}' incompatible with values {incompatible}"
            )

        return self

    unit: Optional[Union[Literal["arbitrary unit"], SiUnit]] = None

    @property
    def range(self):
        if isinstance(self.values[0], str):
            return 0, len(self.values) - 1
        else:
            return min(self.values), max(self.values)


IntervalOrRatioDType = Literal[
    "float32",
    "float64",
    "uint8",
    "int8",
    "uint16",
    "int16",
    "uint32",
    "int32",
    "uint64",
    "int64",
]


class IntervalOrRatioDataDescr(Node):
    type: Annotated[  # TODO: rename to dtype
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
    `None` corresponds to min/max of what can be expressed by **type**."""
    unit: Union[Literal["arbitrary unit"], SiUnit] = "arbitrary unit"
    scale: float = 1.0
    """Scale for data on an interval (or ratio) scale."""
    offset: Optional[float] = None
    """Offset for data on a ratio scale."""

    @model_validator(mode="before")
    def _replace_inf(cls, data: Any):
        if is_dict(data):
            if "range" in data and is_sequence(data["range"]):
                forbidden = (
                    "inf",
                    "-inf",
                    ".inf",
                    "-.inf",
                    float("inf"),
                    float("-inf"),
                )
                if any(v in forbidden for v in data["range"]):
                    issue_warning("replaced 'inf' value", value=data["range"])

                data["range"] = tuple(
                    (None if v in forbidden else v) for v in data["range"]
                )

        return data


TensorDataDescr = Union[NominalOrOrdinalDataDescr, IntervalOrRatioDataDescr]


class ProcessingDescrBase(NodeWithExplicitlySetFields, ABC):
    """processing base class"""


class BinarizeKwargs(ProcessingKwargs):
    """key word arguments for `BinarizeDescr`"""

    threshold: float
    """The fixed threshold"""


class BinarizeAlongAxisKwargs(ProcessingKwargs):
    """key word arguments for `BinarizeDescr`"""

    threshold: NotEmpty[List[float]]
    """The fixed threshold values along `axis`"""

    axis: Annotated[NonBatchAxisId, Field(examples=["channel"])]
    """The `threshold` axis"""


class BinarizeDescr(ProcessingDescrBase):
    """Binarize the tensor with a fixed threshold.

    Values above `BinarizeKwargs.threshold`/`BinarizeAlongAxisKwargs.threshold`
    will be set to one, values below the threshold to zero.

    Examples:
    - in YAML
        ```yaml
        postprocessing:
          - id: binarize
            kwargs:
              axis: 'channel'
              threshold: [0.25, 0.5, 0.75]
        ```
    - in Python:
        >>> postprocessing = [BinarizeDescr(
        ...   kwargs=BinarizeAlongAxisKwargs(
        ...       axis=AxisId('channel'),
        ...       threshold=[0.25, 0.5, 0.75],
        ...   )
        ... )]
    """

    implemented_id: ClassVar[Literal["binarize"]] = "binarize"
    if TYPE_CHECKING:
        id: Literal["binarize"] = "binarize"
    else:
        id: Literal["binarize"]
    kwargs: Union[BinarizeKwargs, BinarizeAlongAxisKwargs]


class ClipDescr(ProcessingDescrBase):
    """Set tensor values below min to min and above max to max.

    See `ScaleRangeDescr` for examples.
    """

    implemented_id: ClassVar[Literal["clip"]] = "clip"
    if TYPE_CHECKING:
        id: Literal["clip"] = "clip"
    else:
        id: Literal["clip"]

    kwargs: ClipKwargs


class EnsureDtypeKwargs(ProcessingKwargs):
    """key word arguments for `EnsureDtypeDescr`"""

    dtype: Literal[
        "float32",
        "float64",
        "uint8",
        "int8",
        "uint16",
        "int16",
        "uint32",
        "int32",
        "uint64",
        "int64",
        "bool",
    ]


class EnsureDtypeDescr(ProcessingDescrBase):
    """Cast the tensor data type to `EnsureDtypeKwargs.dtype` (if not matching).

    This can for example be used to ensure the inner neural network model gets a
    different input tensor data type than the fully described bioimage.io model does.

    Examples:
        The described bioimage.io model (incl. preprocessing) accepts any
        float32-compatible tensor, normalizes it with percentiles and clipping and then
        casts it to uint8, which is what the neural network in this example expects.
        - in YAML
            ```yaml
            inputs:
            - data:
                type: float32  # described bioimage.io model is compatible with any float32 input tensor
              preprocessing:
              - id: scale_range
                  kwargs:
                  axes: ['y', 'x']
                  max_percentile: 99.8
                  min_percentile: 5.0
              - id: clip
                  kwargs:
                  min: 0.0
                  max: 1.0
              - id: ensure_dtype  # the neural network of the model requires uint8
                  kwargs:
                  dtype: uint8
            ```
        - in Python:
            >>> preprocessing = [
            ...     ScaleRangeDescr(
            ...         kwargs=ScaleRangeKwargs(
            ...           axes= (AxisId('y'), AxisId('x')),
            ...           max_percentile= 99.8,
            ...           min_percentile= 5.0,
            ...         )
            ...     ),
            ...     ClipDescr(kwargs=ClipKwargs(min=0.0, max=1.0)),
            ...     EnsureDtypeDescr(kwargs=EnsureDtypeKwargs(dtype="uint8")),
            ... ]
    """

    implemented_id: ClassVar[Literal["ensure_dtype"]] = "ensure_dtype"
    if TYPE_CHECKING:
        id: Literal["ensure_dtype"] = "ensure_dtype"
    else:
        id: Literal["ensure_dtype"]

    kwargs: EnsureDtypeKwargs


class ScaleLinearKwargs(ProcessingKwargs):
    """Key word arguments for `ScaleLinearDescr`"""

    gain: float = 1.0
    """multiplicative factor"""

    offset: float = 0.0
    """additive term"""

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.gain == 1.0 and self.offset == 0.0:
            raise ValueError(
                "Redundant linear scaling not allowd. Set `gain` != 1.0 and/or `offset`"
                + " != 0.0."
            )

        return self


class ScaleLinearAlongAxisKwargs(ProcessingKwargs):
    """Key word arguments for `ScaleLinearDescr`"""

    axis: Annotated[NonBatchAxisId, Field(examples=["channel"])]
    """The axis of gain and offset values."""

    gain: Union[float, NotEmpty[List[float]]] = 1.0
    """multiplicative factor"""

    offset: Union[float, NotEmpty[List[float]]] = 0.0
    """additive term"""

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if isinstance(self.gain, list):
            if isinstance(self.offset, list):
                if len(self.gain) != len(self.offset):
                    raise ValueError(
                        f"Size of `gain` ({len(self.gain)}) and `offset` ({len(self.offset)}) must match."
                    )
            else:
                self.offset = [float(self.offset)] * len(self.gain)
        elif isinstance(self.offset, list):
            self.gain = [float(self.gain)] * len(self.offset)
        else:
            raise ValueError(
                "Do not specify an `axis` for scalar gain and offset values."
            )

        if all(g == 1.0 for g in self.gain) and all(off == 0.0 for off in self.offset):
            raise ValueError(
                "Redundant linear scaling not allowd. Set `gain` != 1.0 and/or `offset`"
                + " != 0.0."
            )

        return self


class ScaleLinearDescr(ProcessingDescrBase):
    """Fixed linear scaling.

    Examples:
      1. Scale with scalar gain and offset
        - in YAML
        ```yaml
        preprocessing:
          - id: scale_linear
            kwargs:
              gain: 2.0
              offset: 3.0
        ```
        - in Python:
        >>> preprocessing = [
        ...     ScaleLinearDescr(kwargs=ScaleLinearKwargs(gain= 2.0, offset=3.0))
        ... ]

      2. Independent scaling along an axis
        - in YAML
        ```yaml
        preprocessing:
          - id: scale_linear
            kwargs:
              axis: 'channel'
              gain: [1.0, 2.0, 3.0]
        ```
        - in Python:
        >>> preprocessing = [
        ...     ScaleLinearDescr(
        ...         kwargs=ScaleLinearAlongAxisKwargs(
        ...             axis=AxisId("channel"),
        ...             gain=[1.0, 2.0, 3.0],
        ...         )
        ...     )
        ... ]

    """

    implemented_id: ClassVar[Literal["scale_linear"]] = "scale_linear"
    if TYPE_CHECKING:
        id: Literal["scale_linear"] = "scale_linear"
    else:
        id: Literal["scale_linear"]
    kwargs: Union[ScaleLinearKwargs, ScaleLinearAlongAxisKwargs]


class SigmoidDescr(ProcessingDescrBase):
    """The logistic sigmoid function, a.k.a. expit function.

    Examples:
    - in YAML
        ```yaml
        postprocessing:
          - id: sigmoid
        ```
    - in Python:
        >>> postprocessing = [SigmoidDescr()]
    """

    implemented_id: ClassVar[Literal["sigmoid"]] = "sigmoid"
    if TYPE_CHECKING:
        id: Literal["sigmoid"] = "sigmoid"
    else:
        id: Literal["sigmoid"]

    @property
    def kwargs(self) -> ProcessingKwargs:
        """empty kwargs"""
        return ProcessingKwargs()


class SoftmaxKwargs(ProcessingKwargs):
    """key word arguments for `SoftmaxDescr`"""

    axis: Annotated[NonBatchAxisId, Field(examples=["channel"])] = AxisId("channel")
    """The axis to apply the softmax function along.
    Note:
        Defaults to 'channel' axis
        (which may not exist, in which case
        a different axis id has to be specified).
    """


class SoftmaxDescr(ProcessingDescrBase):
    """The softmax function.

    Examples:
    - in YAML
        ```yaml
        postprocessing:
          - id: softmax
            kwargs:
              axis: channel
        ```
    - in Python:
        >>> postprocessing = [SoftmaxDescr(kwargs=SoftmaxKwargs(axis=AxisId("channel")))]
    """

    implemented_id: ClassVar[Literal["softmax"]] = "softmax"
    if TYPE_CHECKING:
        id: Literal["softmax"] = "softmax"
    else:
        id: Literal["softmax"]

    kwargs: SoftmaxKwargs = Field(default_factory=SoftmaxKwargs.model_construct)


class FixedZeroMeanUnitVarianceKwargs(ProcessingKwargs):
    """key word arguments for `FixedZeroMeanUnitVarianceDescr`"""

    mean: float
    """The mean value to normalize with."""

    std: Annotated[float, Ge(1e-6)]
    """The standard deviation value to normalize with."""


class FixedZeroMeanUnitVarianceAlongAxisKwargs(ProcessingKwargs):
    """key word arguments for `FixedZeroMeanUnitVarianceDescr`"""

    mean: NotEmpty[List[float]]
    """The mean value(s) to normalize with."""

    std: NotEmpty[List[Annotated[float, Ge(1e-6)]]]
    """The standard deviation value(s) to normalize with.
    Size must match `mean` values."""

    axis: Annotated[NonBatchAxisId, Field(examples=["channel", "index"])]
    """The axis of the mean/std values to normalize each entry along that dimension
    separately."""

    @model_validator(mode="after")
    def _mean_and_std_match(self) -> Self:
        if len(self.mean) != len(self.std):
            raise ValueError(
                f"Size of `mean` ({len(self.mean)}) and `std` ({len(self.std)})"
                + " must match."
            )

        return self


class FixedZeroMeanUnitVarianceDescr(ProcessingDescrBase):
    """Subtract a given mean and divide by the standard deviation.

    Normalize with fixed, precomputed values for
    `FixedZeroMeanUnitVarianceKwargs.mean` and `FixedZeroMeanUnitVarianceKwargs.std`
    Use `FixedZeroMeanUnitVarianceAlongAxisKwargs` for independent scaling along given
    axes.

    Examples:
    1. scalar value for whole tensor
        - in YAML
        ```yaml
        preprocessing:
          - id: fixed_zero_mean_unit_variance
            kwargs:
              mean: 103.5
              std: 13.7
        ```
        - in Python
        >>> preprocessing = [FixedZeroMeanUnitVarianceDescr(
        ...   kwargs=FixedZeroMeanUnitVarianceKwargs(mean=103.5, std=13.7)
        ... )]

    2. independently along an axis
        - in YAML
        ```yaml
        preprocessing:
          - id: fixed_zero_mean_unit_variance
            kwargs:
              axis: channel
              mean: [101.5, 102.5, 103.5]
              std: [11.7, 12.7, 13.7]
        ```
        - in Python
        >>> preprocessing = [FixedZeroMeanUnitVarianceDescr(
        ...   kwargs=FixedZeroMeanUnitVarianceAlongAxisKwargs(
        ...     axis=AxisId("channel"),
        ...     mean=[101.5, 102.5, 103.5],
        ...     std=[11.7, 12.7, 13.7],
        ...   )
        ... )]
    """

    implemented_id: ClassVar[Literal["fixed_zero_mean_unit_variance"]] = (
        "fixed_zero_mean_unit_variance"
    )
    if TYPE_CHECKING:
        id: Literal["fixed_zero_mean_unit_variance"] = "fixed_zero_mean_unit_variance"
    else:
        id: Literal["fixed_zero_mean_unit_variance"]

    kwargs: Union[
        FixedZeroMeanUnitVarianceKwargs, FixedZeroMeanUnitVarianceAlongAxisKwargs
    ]


class ZeroMeanUnitVarianceKwargs(ProcessingKwargs):
    """key word arguments for `ZeroMeanUnitVarianceDescr`"""

    axes: Annotated[
        Optional[Sequence[AxisId]], Field(examples=[("batch", "x", "y")])
    ] = None
    """The subset of axes to normalize jointly, i.e. axes to reduce to compute mean/std.
    For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
    To normalize each sample independently leave out the 'batch' axis.
    Default: Scale all axes jointly."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`."""


class ZeroMeanUnitVarianceDescr(ProcessingDescrBase):
    """Subtract mean and divide by variance.

    Examples:
        Subtract tensor mean and variance
        - in YAML
        ```yaml
        preprocessing:
          - id: zero_mean_unit_variance
        ```
        - in Python
        >>> preprocessing = [ZeroMeanUnitVarianceDescr()]
    """

    implemented_id: ClassVar[Literal["zero_mean_unit_variance"]] = (
        "zero_mean_unit_variance"
    )
    if TYPE_CHECKING:
        id: Literal["zero_mean_unit_variance"] = "zero_mean_unit_variance"
    else:
        id: Literal["zero_mean_unit_variance"]

    kwargs: ZeroMeanUnitVarianceKwargs = Field(
        default_factory=ZeroMeanUnitVarianceKwargs.model_construct
    )


class ScaleRangeKwargs(ProcessingKwargs):
    """key word arguments for `ScaleRangeDescr`

    For `min_percentile`=0.0 (the default) and `max_percentile`=100 (the default)
    this processing step normalizes data to the [0, 1] intervall.
    For other percentiles the normalized values will partially be outside the [0, 1]
    intervall. Use `ScaleRange` followed by `ClipDescr` if you want to limit the
    normalized values to a range.
    """

    axes: Annotated[
        Optional[Sequence[AxisId]], Field(examples=[("batch", "x", "y")])
    ] = None
    """The subset of axes to normalize jointly, i.e. axes to reduce to compute the min/max percentile value.
    For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
    To normalize samples independently, leave out the "batch" axis.
    Default: Scale all axes jointly."""

    min_percentile: Annotated[float, Interval(ge=0, lt=100)] = 0.0
    """The lower percentile used to determine the value to align with zero."""

    max_percentile: Annotated[float, Interval(gt=1, le=100)] = 100.0
    """The upper percentile used to determine the value to align with one.
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
    """Scale with percentiles.

    Examples:
    1. Scale linearly to map 5th percentile to 0 and 99.8th percentile to 1.0
        - in YAML
        ```yaml
        preprocessing:
          - id: scale_range
            kwargs:
              axes: ['y', 'x']
              max_percentile: 99.8
              min_percentile: 5.0
        ```
        - in Python
        >>> preprocessing = [
        ...     ScaleRangeDescr(
        ...         kwargs=ScaleRangeKwargs(
        ...           axes= (AxisId('y'), AxisId('x')),
        ...           max_percentile= 99.8,
        ...           min_percentile= 5.0,
        ...         )
        ...     ),
        ...     ClipDescr(
        ...         kwargs=ClipKwargs(
        ...             min=0.0,
        ...             max=1.0,
        ...         )
        ...     ),
        ... ]

      2. Combine the above scaling with additional clipping to clip values outside the range given by the percentiles.
        - in YAML
        ```yaml
        preprocessing:
          - id: scale_range
            kwargs:
              axes: ['y', 'x']
              max_percentile: 99.8
              min_percentile: 5.0
                  - id: scale_range
           - id: clip
             kwargs:
              min: 0.0
              max: 1.0
        ```
        - in Python
        >>> preprocessing = [ScaleRangeDescr(
        ...   kwargs=ScaleRangeKwargs(
        ...       axes= (AxisId('y'), AxisId('x')),
        ...       max_percentile= 99.8,
        ...       min_percentile= 5.0,
        ...   )
        ... )]

    """

    implemented_id: ClassVar[Literal["scale_range"]] = "scale_range"
    if TYPE_CHECKING:
        id: Literal["scale_range"] = "scale_range"
    else:
        id: Literal["scale_range"]
    kwargs: ScaleRangeKwargs = Field(default_factory=ScaleRangeKwargs.model_construct)


class ScaleMeanVarianceKwargs(ProcessingKwargs):
    """key word arguments for `ScaleMeanVarianceKwargs`"""

    reference_tensor: TensorId
    """Name of tensor to match."""

    axes: Annotated[
        Optional[Sequence[AxisId]], Field(examples=[("batch", "x", "y")])
    ] = None
    """The subset of axes to normalize jointly, i.e. axes to reduce to compute mean/std.
    For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
    resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
    To normalize samples independently, leave out the 'batch' axis.
    Default: Scale all axes jointly."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """Epsilon for numeric stability:
    `out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean.`"""


class ScaleMeanVarianceDescr(ProcessingDescrBase):
    """Scale a tensor's data distribution to match another tensor's mean/std.
    `out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean.`
    """

    implemented_id: ClassVar[Literal["scale_mean_variance"]] = "scale_mean_variance"
    if TYPE_CHECKING:
        id: Literal["scale_mean_variance"] = "scale_mean_variance"
    else:
        id: Literal["scale_mean_variance"]
    kwargs: ScaleMeanVarianceKwargs


PreprocessingDescr = Annotated[
    Union[
        BinarizeDescr,
        ClipDescr,
        EnsureDtypeDescr,
        FixedZeroMeanUnitVarianceDescr,
        ScaleLinearDescr,
        ScaleRangeDescr,
        SigmoidDescr,
        SoftmaxDescr,
        ZeroMeanUnitVarianceDescr,
    ],
    Discriminator("id"),
]
PostprocessingDescr = Annotated[
    Union[
        BinarizeDescr,
        ClipDescr,
        EnsureDtypeDescr,
        FixedZeroMeanUnitVarianceDescr,
        ScaleLinearDescr,
        ScaleMeanVarianceDescr,
        ScaleRangeDescr,
        SigmoidDescr,
        SoftmaxDescr,
        ZeroMeanUnitVarianceDescr,
    ],
    Discriminator("id"),
]

IO_AxisT = TypeVar("IO_AxisT", InputAxis, OutputAxis)


class TensorDescrBase(Node, Generic[IO_AxisT]):
    id: TensorId
    """Tensor id. No duplicates are allowed."""

    description: Annotated[str, MaxLen(128)] = ""
    """free text description"""

    axes: NotEmpty[Sequence[IO_AxisT]]
    """tensor axes"""

    @property
    def shape(self):
        return tuple(a.size for a in self.axes)

    @field_validator("axes", mode="after", check_fields=False)
    @classmethod
    def _validate_axes(cls, axes: Sequence[AnyAxis]) -> Sequence[AnyAxis]:
        batch_axes = [a for a in axes if a.type == "batch"]
        if len(batch_axes) > 1:
            raise ValueError(
                f"Only one batch axis (per tensor) allowed, but got {batch_axes}"
            )

        seen_ids: Set[AxisId] = set()
        duplicate_axes_ids: Set[AxisId] = set()
        for a in axes:
            (duplicate_axes_ids if a.id in seen_ids else seen_ids).add(a.id)

        if duplicate_axes_ids:
            raise ValueError(f"Duplicate axis ids: {duplicate_axes_ids}")

        return axes

    test_tensor: FAIR[Optional[FileDescr_]] = None
    """An example tensor to use for testing.
    Using the model with the test input tensors is expected to yield the test output tensors.
    Each test tensor has be a an ndarray in the
    [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
    The file extension must be '.npy'."""

    sample_tensor: FAIR[Optional[FileDescr_]] = None
    """A sample tensor to illustrate a possible input/output for the model,
    The sample image primarily serves to inform a human user about an example use case
    and is typically stored as .hdf5, .png or .tiff.
    It has to be readable by the [imageio library](https://imageio.readthedocs.io/en/stable/formats/index.html#supported-formats)
    (numpy's `.npy` format is not supported).
    The image dimensionality has to match the number of axes specified in this tensor description.
    """

    @model_validator(mode="after")
    def _validate_sample_tensor(self) -> Self:
        if self.sample_tensor is None or not get_validation_context().perform_io_checks:
            return self

        reader = get_reader(self.sample_tensor.source, sha256=self.sample_tensor.sha256)
        tensor: NDArray[Any] = imread(  # pyright: ignore[reportUnknownVariableType]
            reader.read(),
            extension=PurePosixPath(reader.original_file_name).suffix,
        )
        n_dims = len(tensor.squeeze().shape)
        n_dims_min = n_dims_max = len(self.axes)

        for a in self.axes:
            if isinstance(a, BatchAxis):
                n_dims_min -= 1
            elif isinstance(a.size, int):
                if a.size == 1:
                    n_dims_min -= 1
            elif isinstance(a.size, (ParameterizedSize, DataDependentSize)):
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
                f"Expected sample tensor to have {n_dims_min} to"
                + f" {n_dims_max} dimensions, but found {n_dims} (shape: {tensor.shape})."
            )

        return self

    data: Union[TensorDataDescr, NotEmpty[Sequence[TensorDataDescr]]] = (
        IntervalOrRatioDataDescr()
    )
    """Description of the tensor's data values, optionally per channel.
    If specified per channel, the data `type` needs to match across channels."""

    @property
    def dtype(
        self,
    ) -> Literal[
        "float32",
        "float64",
        "uint8",
        "int8",
        "uint16",
        "int16",
        "uint32",
        "int32",
        "uint64",
        "int64",
        "bool",
    ]:
        """dtype as specified under `data.type` or `data[i].type`"""
        if isinstance(self.data, collections.abc.Sequence):
            return self.data[0].type
        else:
            return self.data.type

    @field_validator("data", mode="after")
    @classmethod
    def _check_data_type_across_channels(
        cls, value: Union[TensorDataDescr, NotEmpty[Sequence[TensorDataDescr]]]
    ) -> Union[TensorDataDescr, NotEmpty[Sequence[TensorDataDescr]]]:
        if not isinstance(value, list):
            return value

        dtypes = {t.type for t in value}
        if len(dtypes) > 1:
            raise ValueError(
                "Tensor data descriptions per channel need to agree in their data"
                + f" `type`, but found {dtypes}."
            )

        return value

    @model_validator(mode="after")
    def _check_data_matches_channelaxis(self) -> Self:
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
                f"Got tensor data descriptions for {len(self.data)} channels, but"
                + f" '{a.id}' axis has size {size}."
            )

        return self

    def get_axis_sizes_for_array(self, array: NDArray[Any]) -> Dict[AxisId, int]:
        if len(array.shape) != len(self.axes):
            raise ValueError(
                f"Dimension mismatch: array shape {array.shape} (#{len(array.shape)})"
                + f" incompatible with {len(self.axes)} axes."
            )
        return {a.id: array.shape[i] for i, a in enumerate(self.axes)}


class InputTensorDescr(TensorDescrBase[InputAxis]):
    id: TensorId = TensorId("input")
    """Input tensor id.
    No duplicates are allowed across all inputs and outputs."""

    optional: bool = False
    """indicates that this tensor may be `None`"""

    preprocessing: List[PreprocessingDescr] = Field(
        default_factory=cast(Callable[[], List[PreprocessingDescr]], list)
    )

    """Description of how this input should be preprocessed.

    notes:
    - If preprocessing does not start with an 'ensure_dtype' entry, it is added
      to ensure an input tensor's data type matches the input tensor's data description.
    - If preprocessing does not end with an 'ensure_dtype' or 'binarize' entry, an
      'ensure_dtype' step is added to ensure preprocessing steps are not unintentionally
      changing the data type.
    """

    @model_validator(mode="after")
    def _validate_preprocessing_kwargs(self) -> Self:
        axes_ids = [a.id for a in self.axes]
        for p in self.preprocessing:
            kwargs_axes: Optional[Sequence[Any]] = p.kwargs.get("axes")
            if kwargs_axes is None:
                continue

            if not isinstance(kwargs_axes, collections.abc.Sequence):
                raise ValueError(
                    f"Expected `preprocessing.i.kwargs.axes` to be a sequence, but got {type(kwargs_axes)}"
                )

            if any(a not in axes_ids for a in kwargs_axes):
                raise ValueError(
                    "`preprocessing.i.kwargs.axes` needs to be subset of axes ids"
                )

        if isinstance(self.data, (NominalOrOrdinalDataDescr, IntervalOrRatioDataDescr)):
            dtype = self.data.type
        else:
            dtype = self.data[0].type

        # ensure `preprocessing` begins with `EnsureDtypeDescr`
        if not self.preprocessing or not isinstance(
            self.preprocessing[0], EnsureDtypeDescr
        ):
            self.preprocessing.insert(
                0, EnsureDtypeDescr(kwargs=EnsureDtypeKwargs(dtype=dtype))
            )

        # ensure `preprocessing` ends with `EnsureDtypeDescr` or `BinarizeDescr`
        if not isinstance(self.preprocessing[-1], (EnsureDtypeDescr, BinarizeDescr)):
            self.preprocessing.append(
                EnsureDtypeDescr(kwargs=EnsureDtypeKwargs(dtype=dtype))
            )

        return self


def convert_axes(
    axes: str,
    *,
    shape: Union[
        Sequence[int], _ParameterizedInputShape_v0_4, _ImplicitOutputShape_v0_4
    ],
    tensor_type: Literal["input", "output"],
    halo: Optional[Sequence[int]],
    size_refs: Mapping[_TensorName_v0_4, Mapping[str, int]],
):
    ret: List[AnyAxis] = []
    for i, a in enumerate(axes):
        axis_type = _AXIS_TYPE_MAP.get(a, a)
        if axis_type == "batch":
            ret.append(BatchAxis())
            continue

        scale = 1.0
        if isinstance(shape, _ParameterizedInputShape_v0_4):
            if shape.step[i] == 0:
                size = shape.min[i]
            else:
                size = ParameterizedSize(min=shape.min[i], step=shape.step[i])
        elif isinstance(shape, _ImplicitOutputShape_v0_4):
            ref_t = str(shape.reference_tensor)
            if ref_t.count(".") == 1:
                t_id, orig_a_id = ref_t.split(".")
            else:
                t_id = ref_t
                orig_a_id = a

            a_id = _AXIS_ID_MAP.get(orig_a_id, a)
            if not (orig_scale := shape.scale[i]):
                # old way to insert a new axis dimension
                size = int(2 * shape.offset[i])
            else:
                scale = 1 / orig_scale
                if axis_type in ("channel", "index"):
                    # these axes no longer have a scale
                    offset_from_scale = orig_scale * size_refs.get(
                        _TensorName_v0_4(t_id), {}
                    ).get(orig_a_id, 0)
                else:
                    offset_from_scale = 0
                size = SizeReference(
                    tensor_id=TensorId(t_id),
                    axis_id=AxisId(a_id),
                    offset=int(offset_from_scale + 2 * shape.offset[i]),
                )
        else:
            size = shape[i]

        if axis_type == "time":
            if tensor_type == "input":
                ret.append(TimeInputAxis(size=size, scale=scale))
            else:
                assert not isinstance(size, ParameterizedSize)
                if halo is None:
                    ret.append(TimeOutputAxis(size=size, scale=scale))
                else:
                    assert not isinstance(size, int)
                    ret.append(
                        TimeOutputAxisWithHalo(size=size, scale=scale, halo=halo[i])
                    )

        elif axis_type == "index":
            if tensor_type == "input":
                ret.append(IndexInputAxis(size=size))
            else:
                if isinstance(size, ParameterizedSize):
                    size = DataDependentSize(min=size.min)

                ret.append(IndexOutputAxis(size=size))
        elif axis_type == "channel":
            assert not isinstance(size, ParameterizedSize)
            if isinstance(size, SizeReference):
                warnings.warn(
                    "Conversion of channel size from an implicit output shape may be"
                    + " wrong"
                )
                ret.append(
                    ChannelAxis(
                        channel_names=[
                            Identifier(f"channel{i}") for i in range(size.offset)
                        ]
                    )
                )
            else:
                ret.append(
                    ChannelAxis(
                        channel_names=[Identifier(f"channel{i}") for i in range(size)]
                    )
                )
        elif axis_type == "space":
            if tensor_type == "input":
                ret.append(SpaceInputAxis(id=AxisId(a), size=size, scale=scale))
            else:
                assert not isinstance(size, ParameterizedSize)
                if halo is None or halo[i] == 0:
                    ret.append(SpaceOutputAxis(id=AxisId(a), size=size, scale=scale))
                elif isinstance(size, int):
                    raise NotImplementedError(
                        f"output axis with halo and fixed size (here {size}) not allowed"
                    )
                else:
                    ret.append(
                        SpaceOutputAxisWithHalo(
                            id=AxisId(a), size=size, scale=scale, halo=halo[i]
                        )
                    )

    return ret


def _axes_letters_to_ids(
    axes: Optional[str],
) -> Optional[List[AxisId]]:
    if axes is None:
        return None

    return [AxisId(a) for a in axes]


def _get_complement_v04_axis(
    tensor_axes: Sequence[str], axes: Optional[Sequence[str]]
) -> Optional[AxisId]:
    if axes is None:
        return None

    non_complement_axes = set(axes) | {"b"}
    complement_axes = [a for a in tensor_axes if a not in non_complement_axes]
    if len(complement_axes) > 1:
        raise ValueError(
            f"Expected none or a single complement axis, but axes '{axes}' "
            + f"for tensor dims '{tensor_axes}' leave '{complement_axes}'."
        )

    return None if not complement_axes else AxisId(complement_axes[0])


def _convert_proc(
    p: Union[_PreprocessingDescr_v0_4, _PostprocessingDescr_v0_4],
    tensor_axes: Sequence[str],
) -> Union[PreprocessingDescr, PostprocessingDescr]:
    if isinstance(p, _BinarizeDescr_v0_4):
        return BinarizeDescr(kwargs=BinarizeKwargs(threshold=p.kwargs.threshold))
    elif isinstance(p, _ClipDescr_v0_4):
        return ClipDescr(kwargs=ClipKwargs(min=p.kwargs.min, max=p.kwargs.max))
    elif isinstance(p, _SigmoidDescr_v0_4):
        return SigmoidDescr()
    elif isinstance(p, _ScaleLinearDescr_v0_4):
        axes = _axes_letters_to_ids(p.kwargs.axes)
        if p.kwargs.axes is None:
            axis = None
        else:
            axis = _get_complement_v04_axis(tensor_axes, p.kwargs.axes)

        if axis is None:
            assert not isinstance(p.kwargs.gain, list)
            assert not isinstance(p.kwargs.offset, list)
            kwargs = ScaleLinearKwargs(gain=p.kwargs.gain, offset=p.kwargs.offset)
        else:
            kwargs = ScaleLinearAlongAxisKwargs(
                axis=axis, gain=p.kwargs.gain, offset=p.kwargs.offset
            )
        return ScaleLinearDescr(kwargs=kwargs)
    elif isinstance(p, _ScaleMeanVarianceDescr_v0_4):
        return ScaleMeanVarianceDescr(
            kwargs=ScaleMeanVarianceKwargs(
                axes=_axes_letters_to_ids(p.kwargs.axes),
                reference_tensor=TensorId(str(p.kwargs.reference_tensor)),
                eps=p.kwargs.eps,
            )
        )
    elif isinstance(p, _ZeroMeanUnitVarianceDescr_v0_4):
        if p.kwargs.mode == "fixed":
            mean = p.kwargs.mean
            std = p.kwargs.std
            assert mean is not None
            assert std is not None

            axis = _get_complement_v04_axis(tensor_axes, p.kwargs.axes)

            if axis is None:
                if isinstance(mean, list):
                    raise ValueError("Expected single float value for mean, not <list>")
                if isinstance(std, list):
                    raise ValueError("Expected single float value for std, not <list>")
                return FixedZeroMeanUnitVarianceDescr(
                    kwargs=FixedZeroMeanUnitVarianceKwargs.model_construct(
                        mean=mean,
                        std=std,
                    )
                )
            else:
                if not isinstance(mean, list):
                    mean = [float(mean)]
                if not isinstance(std, list):
                    std = [float(std)]

                return FixedZeroMeanUnitVarianceDescr(
                    kwargs=FixedZeroMeanUnitVarianceAlongAxisKwargs(
                        axis=axis, mean=mean, std=std
                    )
                )

        else:
            axes = _axes_letters_to_ids(p.kwargs.axes) or []
            if p.kwargs.mode == "per_dataset":
                axes = [AxisId("batch")] + axes
            if not axes:
                axes = None
            return ZeroMeanUnitVarianceDescr(
                kwargs=ZeroMeanUnitVarianceKwargs(axes=axes, eps=p.kwargs.eps)
            )

    elif isinstance(p, _ScaleRangeDescr_v0_4):
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
    Converter[
        _InputTensorDescr_v0_4,
        InputTensorDescr,
        FileSource_,
        Optional[FileSource_],
        Mapping[_TensorName_v0_4, Mapping[str, int]],
    ]
):
    def _convert(
        self,
        src: _InputTensorDescr_v0_4,
        tgt: "type[InputTensorDescr] | type[dict[str, Any]]",
        test_tensor: FileSource_,
        sample_tensor: Optional[FileSource_],
        size_refs: Mapping[_TensorName_v0_4, Mapping[str, int]],
    ) -> "InputTensorDescr | dict[str, Any]":
        axes: List[InputAxis] = convert_axes(  # pyright: ignore[reportAssignmentType]
            src.axes,
            shape=src.shape,
            tensor_type="input",
            halo=None,
            size_refs=size_refs,
        )
        prep: List[PreprocessingDescr] = []
        for p in src.preprocessing:
            cp = _convert_proc(p, src.axes)
            assert not isinstance(cp, ScaleMeanVarianceDescr)
            prep.append(cp)

        prep.append(EnsureDtypeDescr(kwargs=EnsureDtypeKwargs(dtype="float32")))

        return tgt(
            axes=axes,
            id=TensorId(str(src.name)),
            test_tensor=FileDescr(source=test_tensor),
            sample_tensor=(
                None if sample_tensor is None else FileDescr(source=sample_tensor)
            ),
            data=dict(type=src.data_type),  # pyright: ignore[reportArgumentType]
            preprocessing=prep,
        )


_input_tensor_conv = _InputTensorConv(_InputTensorDescr_v0_4, InputTensorDescr)


class OutputTensorDescr(TensorDescrBase[OutputAxis]):
    id: TensorId = TensorId("output")
    """Output tensor id.
    No duplicates are allowed across all inputs and outputs."""

    postprocessing: List[PostprocessingDescr] = Field(
        default_factory=cast(Callable[[], List[PostprocessingDescr]], list)
    )
    """Description of how this output should be postprocessed.

    note: `postprocessing` always ends with an 'ensure_dtype' operation.
          If not given this is added to cast to this tensor's `data.type`.
    """

    @model_validator(mode="after")
    def _validate_postprocessing_kwargs(self) -> Self:
        axes_ids = [a.id for a in self.axes]
        for p in self.postprocessing:
            kwargs_axes: Optional[Sequence[Any]] = p.kwargs.get("axes")
            if kwargs_axes is None:
                continue

            if not isinstance(kwargs_axes, collections.abc.Sequence):
                raise ValueError(
                    f"expected `axes` sequence, but got {type(kwargs_axes)}"
                )

            if any(a not in axes_ids for a in kwargs_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes ids")

        if isinstance(self.data, (NominalOrOrdinalDataDescr, IntervalOrRatioDataDescr)):
            dtype = self.data.type
        else:
            dtype = self.data[0].type

        # ensure `postprocessing` ends with `EnsureDtypeDescr` or `BinarizeDescr`
        if not self.postprocessing or not isinstance(
            self.postprocessing[-1], (EnsureDtypeDescr, BinarizeDescr)
        ):
            self.postprocessing.append(
                EnsureDtypeDescr(kwargs=EnsureDtypeKwargs(dtype=dtype))
            )
        return self


class _OutputTensorConv(
    Converter[
        _OutputTensorDescr_v0_4,
        OutputTensorDescr,
        FileSource_,
        Optional[FileSource_],
        Mapping[_TensorName_v0_4, Mapping[str, int]],
    ]
):
    def _convert(
        self,
        src: _OutputTensorDescr_v0_4,
        tgt: "type[OutputTensorDescr] | type[dict[str, Any]]",
        test_tensor: FileSource_,
        sample_tensor: Optional[FileSource_],
        size_refs: Mapping[_TensorName_v0_4, Mapping[str, int]],
    ) -> "OutputTensorDescr | dict[str, Any]":
        # TODO: split convert_axes into convert_output_axes and convert_input_axes
        axes: List[OutputAxis] = convert_axes(  # pyright: ignore[reportAssignmentType]
            src.axes,
            shape=src.shape,
            tensor_type="output",
            halo=src.halo,
            size_refs=size_refs,
        )
        data_descr: Dict[str, Any] = dict(type=src.data_type)
        if data_descr["type"] == "bool":
            data_descr["values"] = [False, True]

        return tgt(
            axes=axes,
            id=TensorId(str(src.name)),
            test_tensor=FileDescr(source=test_tensor),
            sample_tensor=(
                None if sample_tensor is None else FileDescr(source=sample_tensor)
            ),
            data=data_descr,  # pyright: ignore[reportArgumentType]
            postprocessing=[_convert_proc(p, src.axes) for p in src.postprocessing],
        )


_output_tensor_conv = _OutputTensorConv(_OutputTensorDescr_v0_4, OutputTensorDescr)


TensorDescr = Union[InputTensorDescr, OutputTensorDescr]


def validate_tensors(
    tensors: Mapping[TensorId, Tuple[TensorDescr, Optional[NDArray[Any]]]],
    tensor_origin: Literal[
        "test_tensor"
    ],  # for more precise error messages, e.g. 'test_tensor'
):
    all_tensor_axes: Dict[TensorId, Dict[AxisId, Tuple[AnyAxis, Optional[int]]]] = {}

    def e_msg(d: TensorDescr):
        return f"{'inputs' if isinstance(d, InputTensorDescr) else 'outputs'}[{d.id}]"

    for descr, array in tensors.values():
        if array is None:
            axis_sizes = {a.id: None for a in descr.axes}
        else:
            try:
                axis_sizes = descr.get_axis_sizes_for_array(array)
            except ValueError as e:
                raise ValueError(f"{e_msg(descr)} {e}")

        all_tensor_axes[descr.id] = {a.id: (a, axis_sizes[a.id]) for a in descr.axes}

    for descr, array in tensors.values():
        if array is None:
            continue

        if descr.dtype in ("float32", "float64"):
            invalid_test_tensor_dtype = array.dtype.name not in (
                "float32",
                "float64",
                "uint8",
                "int8",
                "uint16",
                "int16",
                "uint32",
                "int32",
                "uint64",
                "int64",
            )
        else:
            invalid_test_tensor_dtype = array.dtype.name != descr.dtype

        if invalid_test_tensor_dtype:
            raise ValueError(
                f"{e_msg(descr)}.{tensor_origin}.dtype '{array.dtype.name}' does not"
                + f" match described dtype '{descr.dtype}'"
            )

        if array.min() > -1e-4 and array.max() < 1e-4:
            raise ValueError(
                "Output values are too small for reliable testing."
                + f" Values <-1e5 or >=1e5 must be present in {tensor_origin}"
            )

        for a in descr.axes:
            actual_size = all_tensor_axes[descr.id][a.id][1]
            if actual_size is None:
                continue

            if a.size is None:
                continue

            if isinstance(a.size, int):
                if actual_size != a.size:
                    raise ValueError(
                        f"{e_msg(descr)}.{tensor_origin}: axis '{a.id}' "
                        + f"has incompatible size {actual_size}, expected {a.size}"
                    )
            elif isinstance(a.size, ParameterizedSize):
                _ = a.size.validate_size(actual_size)
            elif isinstance(a.size, DataDependentSize):
                _ = a.size.validate_size(actual_size)
            elif isinstance(a.size, SizeReference):
                ref_tensor_axes = all_tensor_axes.get(a.size.tensor_id)
                if ref_tensor_axes is None:
                    raise ValueError(
                        f"{e_msg(descr)}.axes[{a.id}].size.tensor_id: Unknown tensor"
                        + f" reference '{a.size.tensor_id}'"
                    )

                ref_axis, ref_size = ref_tensor_axes.get(a.size.axis_id, (None, None))
                if ref_axis is None or ref_size is None:
                    raise ValueError(
                        f"{e_msg(descr)}.axes[{a.id}].size.axis_id: Unknown tensor axis"
                        + f" reference '{a.size.tensor_id}.{a.size.axis_id}"
                    )

                if a.unit != ref_axis.unit:
                    raise ValueError(
                        f"{e_msg(descr)}.axes[{a.id}].size: `SizeReference` requires"
                        + " axis and reference axis to have the same `unit`, but"
                        + f" {a.unit}!={ref_axis.unit}"
                    )

                if actual_size != (
                    expected_size := (
                        ref_size * ref_axis.scale / a.scale + a.size.offset
                    )
                ):
                    raise ValueError(
                        f"{e_msg(descr)}.{tensor_origin}: axis '{a.id}' of size"
                        + f" {actual_size} invalid for referenced size {ref_size};"
                        + f" expected {expected_size}"
                    )
            else:
                assert_never(a.size)


FileDescr_dependencies = Annotated[
    FileDescr_,
    WithSuffix((".yaml", ".yml"), case_sensitive=True),
    Field(examples=[dict(source="environment.yaml")]),
]


class _ArchitectureCallableDescr(Node):
    callable: Annotated[Identifier, Field(examples=["MyNetworkClass", "get_my_model"])]
    """Identifier of the callable that returns a torch.nn.Module instance."""

    kwargs: Dict[str, YamlValue] = Field(
        default_factory=cast(Callable[[], Dict[str, YamlValue]], dict)
    )
    """key word arguments for the `callable`"""


class ArchitectureFromFileDescr(_ArchitectureCallableDescr, FileDescr):
    source: Annotated[FileSource, AfterValidator(wo_special_file_name)]
    """Architecture source file"""

    @model_serializer(mode="wrap", when_used="unless-none")
    def _serialize(self, nxt: SerializerFunctionWrapHandler, info: SerializationInfo):
        return package_file_descr_serializer(self, nxt, info)


class ArchitectureFromLibraryDescr(_ArchitectureCallableDescr):
    import_from: str
    """Where to import the callable from, i.e. `from <import_from> import <callable>`"""


class _ArchFileConv(
    Converter[
        _CallableFromFile_v0_4,
        ArchitectureFromFileDescr,
        Optional[Sha256],
        Dict[str, Any],
    ]
):
    def _convert(
        self,
        src: _CallableFromFile_v0_4,
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
            callable=Identifier(callable_),
            source=cast(FileSource_, source),
            sha256=sha256,
            kwargs=kwargs,
        )


_arch_file_conv = _ArchFileConv(_CallableFromFile_v0_4, ArchitectureFromFileDescr)


class _ArchLibConv(
    Converter[
        _CallableFromDepencency_v0_4, ArchitectureFromLibraryDescr, Dict[str, Any]
    ]
):
    def _convert(
        self,
        src: _CallableFromDepencency_v0_4,
        tgt: "type[ArchitectureFromLibraryDescr | dict[str, Any]]",
        kwargs: Dict[str, Any],
    ) -> "ArchitectureFromLibraryDescr | dict[str, Any]":
        *mods, callable_ = src.split(".")
        import_from = ".".join(mods)
        return tgt(
            import_from=import_from, callable=Identifier(callable_), kwargs=kwargs
        )


_arch_lib_conv = _ArchLibConv(
    _CallableFromDepencency_v0_4, ArchitectureFromLibraryDescr
)


class WeightsEntryDescrBase(FileDescr):
    type: ClassVar[WeightsFormat]
    weights_format_name: ClassVar[str]  # human readable

    source: Annotated[FileSource, AfterValidator(wo_special_file_name)]
    """Source of the weights file."""

    authors: Optional[List[Author]] = None
    """Authors
    Either the person(s) that have trained this model resulting in the original weights file.
        (If this is the initial weights entry, i.e. it does not have a `parent`)
    Or the person(s) who have converted the weights to this weights format.
        (If this is a child weight, i.e. it has a `parent` field)
    """

    parent: Annotated[
        Optional[WeightsFormat], Field(examples=["pytorch_state_dict"])
    ] = None
    """The source weights these weights were converted from.
    For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
    The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
    All weight entries except one (the initial set of weights resulting from training the model),
    need to have this field."""

    comment: str = ""
    """A comment about this weights entry, for example how these weights were created."""

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.type == self.parent:
            raise ValueError("Weights entry can't be it's own parent.")

        return self

    @model_serializer(mode="wrap", when_used="unless-none")
    def _serialize(self, nxt: SerializerFunctionWrapHandler, info: SerializationInfo):
        return package_file_descr_serializer(self, nxt, info)


class KerasHdf5WeightsDescr(WeightsEntryDescrBase):
    type = "keras_hdf5"
    weights_format_name: ClassVar[str] = "Keras HDF5"
    tensorflow_version: Version
    """TensorFlow version used to create these weights."""


class OnnxWeightsDescr(WeightsEntryDescrBase):
    type = "onnx"
    weights_format_name: ClassVar[str] = "ONNX"
    opset_version: Annotated[int, Ge(7)]
    """ONNX opset version"""


class PytorchStateDictWeightsDescr(WeightsEntryDescrBase):
    type = "pytorch_state_dict"
    weights_format_name: ClassVar[str] = "Pytorch State Dict"
    architecture: Union[ArchitectureFromFileDescr, ArchitectureFromLibraryDescr]
    pytorch_version: Version
    """Version of the PyTorch library used.
    If `architecture.depencencies` is specified it has to include pytorch and any version pinning has to be compatible.
    """
    dependencies: Optional[FileDescr_dependencies] = None
    """Custom depencies beyond pytorch described in a Conda environment file.
    Allows to specify custom dependencies, see conda docs:
    - [Exporting an environment file across platforms](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#exporting-an-environment-file-across-platforms)
    - [Creating an environment file manually](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually)

    The conda environment file should include pytorch and any version pinning has to be compatible with
    **pytorch_version**.
    """


class TensorflowJsWeightsDescr(WeightsEntryDescrBase):
    type = "tensorflow_js"
    weights_format_name: ClassVar[str] = "Tensorflow.js"
    tensorflow_version: Version
    """Version of the TensorFlow library used."""

    source: Annotated[FileSource, AfterValidator(wo_special_file_name)]
    """The multi-file weights.
    All required files/folders should be a zip archive."""


class TensorflowSavedModelBundleWeightsDescr(WeightsEntryDescrBase):
    type = "tensorflow_saved_model_bundle"
    weights_format_name: ClassVar[str] = "Tensorflow Saved Model"
    tensorflow_version: Version
    """Version of the TensorFlow library used."""

    dependencies: Optional[FileDescr_dependencies] = None
    """Custom dependencies beyond tensorflow.
    Should include tensorflow and any version pinning has to be compatible with **tensorflow_version**."""

    source: Annotated[FileSource, AfterValidator(wo_special_file_name)]
    """The multi-file weights.
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
    tensorflow_saved_model_bundle: Optional[TensorflowSavedModelBundleWeightsDescr] = (
        None
    )
    torchscript: Optional[TorchscriptWeightsDescr] = None

    @model_validator(mode="after")
    def check_entries(self) -> Self:
        entries = {wtype for wtype, entry in self if entry is not None}

        if not entries:
            raise ValueError("Missing weights entry")

        entries_wo_parent = {
            wtype
            for wtype, entry in self
            if entry is not None and hasattr(entry, "parent") and entry.parent is None
        }
        if len(entries_wo_parent) != 1:
            issue_warning(
                "Exactly one weights entry may not specify the `parent` field (got"
                + " {value}). That entry is considered the original set of model weights."
                + " Other weight formats are created through conversion of the orignal or"
                + " already converted weights. They have to reference the weights format"
                + " they were converted from as their `parent`.",
                value=len(entries_wo_parent),
                field="weights",
            )

        for wtype, entry in self:
            if entry is None:
                continue

            assert hasattr(entry, "type")
            assert hasattr(entry, "parent")
            assert wtype == entry.type
            if (
                entry.parent is not None and entry.parent not in entries
            ):  # self reference checked for `parent` field
                raise ValueError(
                    f"`weights.{wtype}.parent={entry.parent} not in specified weight"
                    + f" formats: {entries}"
                )

        return self

    def __getitem__(
        self,
        key: Literal[
            "keras_hdf5",
            "onnx",
            "pytorch_state_dict",
            "tensorflow_js",
            "tensorflow_saved_model_bundle",
            "torchscript",
        ],
    ):
        if key == "keras_hdf5":
            ret = self.keras_hdf5
        elif key == "onnx":
            ret = self.onnx
        elif key == "pytorch_state_dict":
            ret = self.pytorch_state_dict
        elif key == "tensorflow_js":
            ret = self.tensorflow_js
        elif key == "tensorflow_saved_model_bundle":
            ret = self.tensorflow_saved_model_bundle
        elif key == "torchscript":
            ret = self.torchscript
        else:
            raise KeyError(key)

        if ret is None:
            raise KeyError(key)

        return ret

    @property
    def available_formats(self):
        return {
            **({} if self.keras_hdf5 is None else {"keras_hdf5": self.keras_hdf5}),
            **({} if self.onnx is None else {"onnx": self.onnx}),
            **(
                {}
                if self.pytorch_state_dict is None
                else {"pytorch_state_dict": self.pytorch_state_dict}
            ),
            **(
                {}
                if self.tensorflow_js is None
                else {"tensorflow_js": self.tensorflow_js}
            ),
            **(
                {}
                if self.tensorflow_saved_model_bundle is None
                else {
                    "tensorflow_saved_model_bundle": self.tensorflow_saved_model_bundle
                }
            ),
            **({} if self.torchscript is None else {"torchscript": self.torchscript}),
        }

    @property
    def missing_formats(self):
        return {
            wf for wf in get_args(WeightsFormat) if wf not in self.available_formats
        }


class ModelId(ResourceId):
    pass


class LinkedModel(LinkedResourceBase):
    """Reference to a bioimage.io model."""

    id: ModelId
    """A valid model `id` from the bioimage.io collection."""


class _DataDepSize(NamedTuple):
    min: StrictInt
    max: Optional[StrictInt]


class _AxisSizes(NamedTuple):
    """the lenghts of all axes of model inputs and outputs"""

    inputs: Dict[Tuple[TensorId, AxisId], int]
    outputs: Dict[Tuple[TensorId, AxisId], Union[int, _DataDepSize]]


class _TensorSizes(NamedTuple):
    """_AxisSizes as nested dicts"""

    inputs: Dict[TensorId, Dict[AxisId, int]]
    outputs: Dict[TensorId, Dict[AxisId, Union[int, _DataDepSize]]]


class ReproducibilityTolerance(Node, extra="allow"):
    """Describes what small numerical differences -- if any -- may be tolerated
    in the generated output when executing in different environments.

    A tensor element *output* is considered mismatched to the **test_tensor** if
    abs(*output* - **test_tensor**) > **absolute_tolerance** + **relative_tolerance** * abs(**test_tensor**).
    (Internally we call [numpy.testing.assert_allclose](https://numpy.org/doc/stable/reference/generated/numpy.testing.assert_allclose.html).)

    Motivation:
        For testing we can request the respective deep learning frameworks to be as
        reproducible as possible by setting seeds and chosing deterministic algorithms,
        but differences in operating systems, available hardware and installed drivers
        may still lead to numerical differences.
    """

    relative_tolerance: RelativeTolerance = 1e-3
    """Maximum relative tolerance of reproduced test tensor."""

    absolute_tolerance: AbsoluteTolerance = 1e-4
    """Maximum absolute tolerance of reproduced test tensor."""

    mismatched_elements_per_million: MismatchedElementsPerMillion = 100
    """Maximum number of mismatched elements/pixels per million to tolerate."""

    output_ids: Sequence[TensorId] = ()
    """Limits the output tensor IDs these reproducibility details apply to."""

    weights_formats: Sequence[WeightsFormat] = ()
    """Limits the weights formats these details apply to."""


class BioimageioConfig(Node, extra="allow"):
    reproducibility_tolerance: Sequence[ReproducibilityTolerance] = ()
    """Tolerances to allow when reproducing the model's test outputs
    from the model's test inputs.
    Only the first entry matching tensor id and weights format is considered.
    """


class Config(Node, extra="allow"):
    bioimageio: BioimageioConfig = Field(
        default_factory=BioimageioConfig.model_construct
    )


class ModelDescr(GenericModelDescrBase):
    """Specification of the fields used in a bioimage.io-compliant RDF to describe AI models with pretrained weights.
    These fields are typically stored in a YAML file which we call a model resource description file (model RDF).
    """

    implemented_format_version: ClassVar[Literal["0.5.5"]] = "0.5.5"
    if TYPE_CHECKING:
        format_version: Literal["0.5.5"] = "0.5.5"
    else:
        format_version: Literal["0.5.5"]
        """Version of the bioimage.io model description specification used.
        When creating a new model always use the latest micro/patch version described here.
        The `format_version` is important for any consumer software to understand how to parse the fields.
        """

    implemented_type: ClassVar[Literal["model"]] = "model"
    if TYPE_CHECKING:
        type: Literal["model"] = "model"
    else:
        type: Literal["model"]
        """Specialized resource type 'model'"""

    id: Optional[ModelId] = None
    """bioimage.io-wide unique resource identifier
    assigned by bioimage.io; version **un**specific."""

    authors: FAIR[List[Author]] = Field(
        default_factory=cast(Callable[[], List[Author]], list)
    )
    """The authors are the creators of the model RDF and the primary points of contact."""

    documentation: FAIR[Optional[FileSource_documentation]] = None
    """URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
    The documentation should include a '#[#] Validation' (sub)section
    with details on how to quantitatively validate the model on unseen data."""

    @field_validator("documentation", mode="after")
    @classmethod
    def _validate_documentation(
        cls, value: Optional[FileSource_documentation]
    ) -> Optional[FileSource_documentation]:
        if not get_validation_context().perform_io_checks or value is None:
            return value

        doc_reader = get_reader(value)
        doc_content = doc_reader.read().decode(encoding="utf-8")
        if not re.search("#.*[vV]alidation", doc_content):
            issue_warning(
                "No '# Validation' (sub)section found in {value}.",
                value=value,
                field="documentation",
            )

        return value

    inputs: NotEmpty[Sequence[InputTensorDescr]]
    """Describes the input tensors expected by this model."""

    @field_validator("inputs", mode="after")
    @classmethod
    def _validate_input_axes(
        cls, inputs: Sequence[InputTensorDescr]
    ) -> Sequence[InputTensorDescr]:
        input_size_refs = cls._get_axes_with_independent_size(inputs)

        for i, ipt in enumerate(inputs):
            valid_independent_refs: Dict[
                Tuple[TensorId, AxisId],
                Tuple[TensorDescr, AnyAxis, Union[int, ParameterizedSize]],
            ] = {
                **{
                    (ipt.id, a.id): (ipt, a, a.size)
                    for a in ipt.axes
                    if not isinstance(a, BatchAxis)
                    and isinstance(a.size, (int, ParameterizedSize))
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
        tensor_id: TensorId,
        a: int,
        axis: AnyAxis,
        valid_independent_refs: Dict[
            Tuple[TensorId, AxisId],
            Tuple[TensorDescr, AnyAxis, Union[int, ParameterizedSize]],
        ],
    ):
        if isinstance(axis, BatchAxis) or isinstance(
            axis.size, (int, ParameterizedSize, DataDependentSize)
        ):
            return
        elif not isinstance(axis.size, SizeReference):
            assert_never(axis.size)

        # validate axis.size SizeReference
        ref = (axis.size.tensor_id, axis.size.axis_id)
        if ref not in valid_independent_refs:
            raise ValueError(
                "Invalid tensor axis reference at"
                + f" {field_name}[{i}].axes[{a}].size: {axis.size}."
            )
        if ref == (tensor_id, axis.id):
            raise ValueError(
                "Self-referencing not allowed for"
                + f" {field_name}[{i}].axes[{a}].size: {axis.size}"
            )
        if axis.type == "channel":
            if valid_independent_refs[ref][1].type != "channel":
                raise ValueError(
                    "A channel axis' size may only reference another fixed size"
                    + " channel axis."
                )
            if isinstance(axis.channel_names, str) and "{i}" in axis.channel_names:
                ref_size = valid_independent_refs[ref][2]
                assert isinstance(ref_size, int), (
                    "channel axis ref (another channel axis) has to specify fixed"
                    + " size"
                )
                generated_channel_names = [
                    Identifier(axis.channel_names.format(i=i))
                    for i in range(1, ref_size + 1)
                ]
                axis.channel_names = generated_channel_names

        if (ax_unit := getattr(axis, "unit", None)) != (
            ref_unit := getattr(valid_independent_refs[ref][1], "unit", None)
        ):
            raise ValueError(
                "The units of an axis and its reference axis need to match, but"
                + f" '{ax_unit}' != '{ref_unit}'."
            )
        ref_axis = valid_independent_refs[ref][1]
        if isinstance(ref_axis, BatchAxis):
            raise ValueError(
                f"Invalid reference axis '{ref_axis.id}' for {tensor_id}.{axis.id}"
                + " (a batch axis is not allowed as reference)."
            )

        if isinstance(axis, WithHalo):
            min_size = axis.size.get_size(axis, ref_axis, n=0)
            if (min_size - 2 * axis.halo) < 1:
                raise ValueError(
                    f"axis {axis.id} with minimum size {min_size} is too small for halo"
                    + f" {axis.halo}."
                )

            input_halo = axis.halo * axis.scale / ref_axis.scale
            if input_halo != int(input_halo) or input_halo % 2 == 1:
                raise ValueError(
                    f"input_halo {input_halo} (output_halo {axis.halo} *"
                    + f" output_scale {axis.scale} / input_scale {ref_axis.scale})"
                    + f"     {tensor_id}.{axis.id}."
                )

    @model_validator(mode="after")
    def _validate_test_tensors(self) -> Self:
        if not get_validation_context().perform_io_checks:
            return self

        test_output_arrays = [
            None if descr.test_tensor is None else load_array(descr.test_tensor)
            for descr in self.outputs
        ]
        test_input_arrays = [
            None if descr.test_tensor is None else load_array(descr.test_tensor)
            for descr in self.inputs
        ]

        tensors = {
            descr.id: (descr, array)
            for descr, array in zip(
                chain(self.inputs, self.outputs), test_input_arrays + test_output_arrays
            )
        }
        validate_tensors(tensors, tensor_origin="test_tensor")

        output_arrays = {
            descr.id: array for descr, array in zip(self.outputs, test_output_arrays)
        }
        for rep_tol in self.config.bioimageio.reproducibility_tolerance:
            if not rep_tol.absolute_tolerance:
                continue

            if rep_tol.output_ids:
                out_arrays = {
                    oid: a
                    for oid, a in output_arrays.items()
                    if oid in rep_tol.output_ids
                }
            else:
                out_arrays = output_arrays

            for out_id, array in out_arrays.items():
                if array is None:
                    continue

                if rep_tol.absolute_tolerance > (max_test_value := array.max()) * 0.01:
                    raise ValueError(
                        "config.bioimageio.reproducibility_tolerance.absolute_tolerance="
                        + f"{rep_tol.absolute_tolerance} > 0.01*{max_test_value}"
                        + f" (1% of the maximum value of the test tensor '{out_id}')"
                    )

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
                        f"`reference_tensor` '{ref}' not found. Valid input tensor"
                        + f" references are: {ipt_refs}."
                    )

        for out in self.outputs:
            for p in out.postprocessing:
                ref = p.kwargs.get("reference_tensor")
                if ref is None:
                    continue

                if ref not in ipt_refs and ref not in out_refs:
                    raise ValueError(
                        f"`reference_tensor` '{ref}' not found. Valid tensor references"
                        + f" are: {ipt_refs | out_refs}."
                    )

        return self

    # TODO: use validate funcs in validate_test_tensors
    # def validate_inputs(self, input_tensors: Mapping[TensorId, NDArray[Any]]) -> Mapping[TensorId, NDArray[Any]]:

    name: Annotated[
        str,
        RestrictCharacters(string.ascii_letters + string.digits + "_+- ()"),
        MinLen(5),
        MaxLen(128),
        warn(MaxLen(64), "Name longer than 64 characters.", INFO),
    ]
    """A human-readable name of this model.
    It should be no longer than 64 characters
    and may only contain letter, number, underscore, minus, parentheses and spaces.
    We recommend to chose a name that refers to the model's task and image modality.
    """

    outputs: NotEmpty[Sequence[OutputTensorDescr]]
    """Describes the output tensors."""

    @field_validator("outputs", mode="after")
    @classmethod
    def _validate_tensor_ids(
        cls, outputs: Sequence[OutputTensorDescr], info: ValidationInfo
    ) -> Sequence[OutputTensorDescr]:
        tensor_ids = [
            t.id for t in info.data.get("inputs", []) + info.data.get("outputs", [])
        ]
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
    def _get_axes_with_parameterized_size(
        io: Union[Sequence[InputTensorDescr], Sequence[OutputTensorDescr]],
    ):
        return {
            f"{t.id}.{a.id}": (t, a, a.size)
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis) and isinstance(a.size, ParameterizedSize)
        }

    @staticmethod
    def _get_axes_with_independent_size(
        io: Union[Sequence[InputTensorDescr], Sequence[OutputTensorDescr]],
    ):
        return {
            (t.id, a.id): (t, a, a.size)
            for t in io
            for a in t.axes
            if not isinstance(a, BatchAxis)
            and isinstance(a.size, (int, ParameterizedSize))
        }

    @field_validator("outputs", mode="after")
    @classmethod
    def _validate_output_axes(
        cls, outputs: List[OutputTensorDescr], info: ValidationInfo
    ) -> List[OutputTensorDescr]:
        input_size_refs = cls._get_axes_with_independent_size(
            info.data.get("inputs", [])
        )
        output_size_refs = cls._get_axes_with_independent_size(outputs)

        for i, out in enumerate(outputs):
            valid_independent_refs: Dict[
                Tuple[TensorId, AxisId],
                Tuple[TensorDescr, AnyAxis, Union[int, ParameterizedSize]],
            ] = {
                **{
                    (out.id, a.id): (out, a, a.size)
                    for a in out.axes
                    if not isinstance(a, BatchAxis)
                    and isinstance(a.size, (int, ParameterizedSize))
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

    packaged_by: List[Author] = Field(
        default_factory=cast(Callable[[], List[Author]], list)
    )
    """The persons that have packaged and uploaded this model.
    Only required if those persons differ from the `authors`."""

    parent: Optional[LinkedModel] = None
    """The model from which this model is derived, e.g. by fine-tuning the weights."""

    @model_validator(mode="after")
    def _validate_parent_is_not_self(self) -> Self:
        if self.parent is not None and self.parent.id == self.id:
            raise ValueError("A model description may not reference itself as parent.")

        return self

    run_mode: Annotated[
        Optional[RunMode],
        warn(None, "Run mode '{value}' has limited support across consumer softwares."),
    ] = None
    """Custom run mode for this model: for more complex prediction procedures like test time
    data augmentation that currently cannot be expressed in the specification.
    No standard run modes are defined yet."""

    timestamp: Datetime = Field(default_factory=Datetime.now)
    """Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
    with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat).
    (In Python a datetime object is valid, too)."""

    training_data: Annotated[
        Union[None, LinkedDataset, DatasetDescr, DatasetDescr02],
        Field(union_mode="left_to_right"),
    ] = None
    """The dataset used to train this model"""

    weights: Annotated[WeightsDescr, WrapSerializer(package_weights)]
    """The weights for this model.
    Weights can be given for different formats, but should otherwise be equivalent.
    The available weight formats determine which consumers can use this model."""

    config: Config = Field(default_factory=Config.model_construct)

    @model_validator(mode="after")
    def _add_default_cover(self) -> Self:
        if not get_validation_context().perform_io_checks or self.covers:
            return self

        try:
            generated_covers = generate_covers(
                [
                    (t, load_array(t.test_tensor))
                    for t in self.inputs
                    if t.test_tensor is not None
                ],
                [
                    (t, load_array(t.test_tensor))
                    for t in self.outputs
                    if t.test_tensor is not None
                ],
            )
        except Exception as e:
            issue_warning(
                "Failed to generate cover image(s): {e}",
                value=self.covers,
                msg_context=dict(e=e),
                field="covers",
            )
        else:
            self.covers.extend(generated_covers)

        return self

    def get_input_test_arrays(self) -> List[NDArray[Any]]:
        return self._get_test_arrays(self.inputs)

    def get_output_test_arrays(self) -> List[NDArray[Any]]:
        return self._get_test_arrays(self.outputs)

    @staticmethod
    def _get_test_arrays(
        io_descr: Union[Sequence[InputTensorDescr], Sequence[OutputTensorDescr]],
    ):
        ts: List[FileDescr] = []
        for d in io_descr:
            if d.test_tensor is None:
                raise ValueError(
                    f"Failed to get test arrays: description of '{d.id}' is missing a `test_tensor`."
                )
            ts.append(d.test_tensor)

        data = [load_array(t) for t in ts]
        assert all(isinstance(d, np.ndarray) for d in data)
        return data

    @staticmethod
    def get_batch_size(tensor_sizes: Mapping[TensorId, Mapping[AxisId, int]]) -> int:
        batch_size = 1
        tensor_with_batchsize: Optional[TensorId] = None
        for tid in tensor_sizes:
            for aid, s in tensor_sizes[tid].items():
                if aid != BATCH_AXIS_ID or s == 1 or s == batch_size:
                    continue

                if batch_size != 1:
                    assert tensor_with_batchsize is not None
                    raise ValueError(
                        f"batch size mismatch for tensors '{tensor_with_batchsize}' ({batch_size}) and '{tid}' ({s})"
                    )

                batch_size = s
                tensor_with_batchsize = tid

        return batch_size

    def get_output_tensor_sizes(
        self, input_sizes: Mapping[TensorId, Mapping[AxisId, int]]
    ) -> Dict[TensorId, Dict[AxisId, Union[int, _DataDepSize]]]:
        """Returns the tensor output sizes for given **input_sizes**.
        Only if **input_sizes** has a valid input shape, the tensor output size is exact.
        Otherwise it might be larger than the actual (valid) output"""
        batch_size = self.get_batch_size(input_sizes)
        ns = self.get_ns(input_sizes)

        tensor_sizes = self.get_tensor_sizes(ns, batch_size=batch_size)
        return tensor_sizes.outputs

    def get_ns(self, input_sizes: Mapping[TensorId, Mapping[AxisId, int]]):
        """get parameter `n` for each parameterized axis
        such that the valid input size is >= the given input size"""
        ret: Dict[Tuple[TensorId, AxisId], ParameterizedSize_N] = {}
        axes = {t.id: {a.id: a for a in t.axes} for t in self.inputs}
        for tid in input_sizes:
            for aid, s in input_sizes[tid].items():
                size_descr = axes[tid][aid].size
                if isinstance(size_descr, ParameterizedSize):
                    ret[(tid, aid)] = size_descr.get_n(s)
                elif size_descr is None or isinstance(size_descr, (int, SizeReference)):
                    pass
                else:
                    assert_never(size_descr)

        return ret

    def get_tensor_sizes(
        self, ns: Mapping[Tuple[TensorId, AxisId], ParameterizedSize_N], batch_size: int
    ) -> _TensorSizes:
        axis_sizes = self.get_axis_sizes(ns, batch_size=batch_size)
        return _TensorSizes(
            {
                t: {
                    aa: axis_sizes.inputs[(tt, aa)]
                    for tt, aa in axis_sizes.inputs
                    if tt == t
                }
                for t in {tt for tt, _ in axis_sizes.inputs}
            },
            {
                t: {
                    aa: axis_sizes.outputs[(tt, aa)]
                    for tt, aa in axis_sizes.outputs
                    if tt == t
                }
                for t in {tt for tt, _ in axis_sizes.outputs}
            },
        )

    def get_axis_sizes(
        self,
        ns: Mapping[Tuple[TensorId, AxisId], ParameterizedSize_N],
        batch_size: Optional[int] = None,
        *,
        max_input_shape: Optional[Mapping[Tuple[TensorId, AxisId], int]] = None,
    ) -> _AxisSizes:
        """Determine input and output block shape for scale factors **ns**
        of parameterized input sizes.

        Args:
            ns: Scale factor `n` for each axis (keyed by (tensor_id, axis_id))
                that is parameterized as `size = min + n * step`.
            batch_size: The desired size of the batch dimension.
                If given **batch_size** overwrites any batch size present in
                **max_input_shape**. Default 1.
            max_input_shape: Limits the derived block shapes.
                Each axis for which the input size, parameterized by `n`, is larger
                than **max_input_shape** is set to the minimal value `n_min` for which
                this is still true.
                Use this for small input samples or large values of **ns**.
                Or simply whenever you know the full input shape.

        Returns:
            Resolved axis sizes for model inputs and outputs.
        """
        max_input_shape = max_input_shape or {}
        if batch_size is None:
            for (_t_id, a_id), s in max_input_shape.items():
                if a_id == BATCH_AXIS_ID:
                    batch_size = s
                    break
            else:
                batch_size = 1

        all_axes = {
            t.id: {a.id: a for a in t.axes} for t in chain(self.inputs, self.outputs)
        }

        inputs: Dict[Tuple[TensorId, AxisId], int] = {}
        outputs: Dict[Tuple[TensorId, AxisId], Union[int, _DataDepSize]] = {}

        def get_axis_size(a: Union[InputAxis, OutputAxis]):
            if isinstance(a, BatchAxis):
                if (t_descr.id, a.id) in ns:
                    logger.warning(
                        "Ignoring unexpected size increment factor (n) for batch axis"
                        + " of tensor '{}'.",
                        t_descr.id,
                    )
                return batch_size
            elif isinstance(a.size, int):
                if (t_descr.id, a.id) in ns:
                    logger.warning(
                        "Ignoring unexpected size increment factor (n) for fixed size"
                        + " axis '{}' of tensor '{}'.",
                        a.id,
                        t_descr.id,
                    )
                return a.size
            elif isinstance(a.size, ParameterizedSize):
                if (t_descr.id, a.id) not in ns:
                    raise ValueError(
                        "Size increment factor (n) missing for parametrized axis"
                        + f" '{a.id}' of tensor '{t_descr.id}'."
                    )
                n = ns[(t_descr.id, a.id)]
                s_max = max_input_shape.get((t_descr.id, a.id))
                if s_max is not None:
                    n = min(n, a.size.get_n(s_max))

                return a.size.get_size(n)

            elif isinstance(a.size, SizeReference):
                if (t_descr.id, a.id) in ns:
                    logger.warning(
                        "Ignoring unexpected size increment factor (n) for axis '{}'"
                        + " of tensor '{}' with size reference.",
                        a.id,
                        t_descr.id,
                    )
                assert not isinstance(a, BatchAxis)
                ref_axis = all_axes[a.size.tensor_id][a.size.axis_id]
                assert not isinstance(ref_axis, BatchAxis)
                ref_key = (a.size.tensor_id, a.size.axis_id)
                ref_size = inputs.get(ref_key, outputs.get(ref_key))
                assert ref_size is not None, ref_key
                assert not isinstance(ref_size, _DataDepSize), ref_key
                return a.size.get_size(
                    axis=a,
                    ref_axis=ref_axis,
                    ref_size=ref_size,
                )
            elif isinstance(a.size, DataDependentSize):
                if (t_descr.id, a.id) in ns:
                    logger.warning(
                        "Ignoring unexpected increment factor (n) for data dependent"
                        + " size axis '{}' of tensor '{}'.",
                        a.id,
                        t_descr.id,
                    )
                return _DataDepSize(a.size.min, a.size.max)
            else:
                assert_never(a.size)

        # first resolve all , but the `SizeReference` input sizes
        for t_descr in self.inputs:
            for a in t_descr.axes:
                if not isinstance(a.size, SizeReference):
                    s = get_axis_size(a)
                    assert not isinstance(s, _DataDepSize)
                    inputs[t_descr.id, a.id] = s

        # resolve all other input axis sizes
        for t_descr in self.inputs:
            for a in t_descr.axes:
                if isinstance(a.size, SizeReference):
                    s = get_axis_size(a)
                    assert not isinstance(s, _DataDepSize)
                    inputs[t_descr.id, a.id] = s

        # resolve all output axis sizes
        for t_descr in self.outputs:
            for a in t_descr.axes:
                assert not isinstance(a.size, ParameterizedSize)
                s = get_axis_size(a)
                outputs[t_descr.id, a.id] = s

        return _AxisSizes(inputs=inputs, outputs=outputs)

    @model_validator(mode="before")
    @classmethod
    def _convert(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        cls.convert_from_old_format_wo_validation(data)
        return data

    @classmethod
    def convert_from_old_format_wo_validation(cls, data: Dict[str, Any]) -> None:
        """Convert metadata following an older format version to this classes' format
        without validating the result.
        """
        if (
            data.get("type") == "model"
            and isinstance(fv := data.get("format_version"), str)
            and fv.count(".") == 2
        ):
            fv_parts = fv.split(".")
            if any(not p.isdigit() for p in fv_parts):
                return

            fv_tuple = tuple(map(int, fv_parts))

            assert cls.implemented_format_version_tuple[0:2] == (0, 5)
            if fv_tuple[:2] in ((0, 3), (0, 4)):
                m04 = _ModelDescr_v0_4.load(data)
                if isinstance(m04, InvalidDescr):
                    try:
                        updated = _model_conv.convert_as_dict(
                            m04  # pyright: ignore[reportArgumentType]
                        )
                    except Exception as e:
                        logger.error(
                            "Failed to convert from invalid model 0.4 description."
                            + f"\nerror: {e}"
                            + "\nProceeding with model 0.5 validation without conversion."
                        )
                        updated = None
                else:
                    updated = _model_conv.convert_as_dict(m04)

                if updated is not None:
                    data.clear()
                    data.update(updated)

            elif fv_tuple[:2] == (0, 5):
                # bump patch version
                data["format_version"] = cls.implemented_format_version


class _ModelConv(Converter[_ModelDescr_v0_4, ModelDescr]):
    def _convert(
        self, src: _ModelDescr_v0_4, tgt: "type[ModelDescr] | type[dict[str, Any]]"
    ) -> "ModelDescr | dict[str, Any]":
        name = "".join(
            c if c in string.ascii_letters + string.digits + "_+- ()" else " "
            for c in src.name
        )

        def conv_authors(auths: Optional[Sequence[_Author_v0_4]]):
            conv = (
                _author_conv.convert if TYPE_CHECKING else _author_conv.convert_as_dict
            )
            return None if auths is None else [conv(a) for a in auths]

        if TYPE_CHECKING:
            arch_file_conv = _arch_file_conv.convert
            arch_lib_conv = _arch_lib_conv.convert
        else:
            arch_file_conv = _arch_file_conv.convert_as_dict
            arch_lib_conv = _arch_lib_conv.convert_as_dict

        input_size_refs = {
            ipt.name: {
                a: s
                for a, s in zip(
                    ipt.axes,
                    (
                        ipt.shape.min
                        if isinstance(ipt.shape, _ParameterizedInputShape_v0_4)
                        else ipt.shape
                    ),
                )
            }
            for ipt in src.inputs
            if ipt.shape
        }
        output_size_refs = {
            **{
                out.name: {a: s for a, s in zip(out.axes, out.shape)}
                for out in src.outputs
                if not isinstance(out.shape, _ImplicitOutputShape_v0_4)
            },
            **input_size_refs,
        }

        return tgt(
            attachments=(
                []
                if src.attachments is None
                else [FileDescr(source=f) for f in src.attachments.files]
            ),
            authors=[_author_conv.convert_as_dict(a) for a in src.authors],  # pyright: ignore[reportArgumentType]
            cite=[{"text": c.text, "doi": c.doi, "url": c.url} for c in src.cite],  # pyright: ignore[reportArgumentType]
            config=src.config,  # pyright: ignore[reportArgumentType]
            covers=src.covers,
            description=src.description,
            documentation=src.documentation,
            format_version="0.5.5",
            git_repo=src.git_repo,  # pyright: ignore[reportArgumentType]
            icon=src.icon,
            id=None if src.id is None else ModelId(src.id),
            id_emoji=src.id_emoji,
            license=src.license,  # type: ignore
            links=src.links,
            maintainers=[_maintainer_conv.convert_as_dict(m) for m in src.maintainers],  # pyright: ignore[reportArgumentType]
            name=name,
            tags=src.tags,
            type=src.type,
            uploader=src.uploader,
            version=src.version,
            inputs=[  # pyright: ignore[reportArgumentType]
                _input_tensor_conv.convert_as_dict(ipt, tt, st, input_size_refs)
                for ipt, tt, st in zip(
                    src.inputs,
                    src.test_inputs,
                    src.sample_inputs or [None] * len(src.test_inputs),
                )
            ],
            outputs=[  # pyright: ignore[reportArgumentType]
                _output_tensor_conv.convert_as_dict(out, tt, st, output_size_refs)
                for out, tt, st in zip(
                    src.outputs,
                    src.test_outputs,
                    src.sample_outputs or [None] * len(src.test_outputs),
                )
            ],
            parent=(
                None
                if src.parent is None
                else LinkedModel(
                    id=ModelId(
                        str(src.parent.id)
                        + (
                            ""
                            if src.parent.version_number is None
                            else f"/{src.parent.version_number}"
                        )
                    )
                )
            ),
            training_data=(
                None
                if src.training_data is None
                else (
                    LinkedDataset(
                        id=DatasetId(
                            str(src.training_data.id)
                            + (
                                ""
                                if src.training_data.version_number is None
                                else f"/{src.training_data.version_number}"
                            )
                        )
                    )
                    if isinstance(src.training_data, LinkedDataset02)
                    else src.training_data
                )
            ),
            packaged_by=[_author_conv.convert_as_dict(a) for a in src.packaged_by],  # pyright: ignore[reportArgumentType]
            run_mode=src.run_mode,
            timestamp=src.timestamp,
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
                    architecture=(
                        arch_file_conv(
                            w.architecture,
                            w.architecture_sha256,
                            w.kwargs,
                        )
                        if isinstance(w.architecture, _CallableFromFile_v0_4)
                        else arch_lib_conv(w.architecture, w.kwargs)
                    ),
                    pytorch_version=w.pytorch_version or Version("1.10"),
                    dependencies=(
                        None
                        if w.dependencies is None
                        else (FileDescr if TYPE_CHECKING else dict)(
                            source=cast(
                                FileSource,
                                str(deps := w.dependencies)[
                                    (
                                        len("conda:")
                                        if str(deps).startswith("conda:")
                                        else 0
                                    ) :
                                ],
                            )
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
                tensorflow_saved_model_bundle=(
                    w := src.weights.tensorflow_saved_model_bundle
                )
                and (TensorflowSavedModelBundleWeightsDescr if TYPE_CHECKING else dict)(
                    authors=conv_authors(w.authors),
                    parent=w.parent,
                    source=w.source,
                    tensorflow_version=w.tensorflow_version or Version("1.15"),
                    dependencies=(
                        None
                        if w.dependencies is None
                        else (FileDescr if TYPE_CHECKING else dict)(
                            source=cast(
                                FileSource,
                                (
                                    str(w.dependencies)[len("conda:") :]
                                    if str(w.dependencies).startswith("conda:")
                                    else str(w.dependencies)
                                ),
                            )
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


_model_conv = _ModelConv(_ModelDescr_v0_4, ModelDescr)


# create better cover images for 3d data and non-image outputs
def generate_covers(
    inputs: Sequence[Tuple[InputTensorDescr, NDArray[Any]]],
    outputs: Sequence[Tuple[OutputTensorDescr, NDArray[Any]]],
) -> List[Path]:
    def squeeze(
        data: NDArray[Any], axes: Sequence[AnyAxis]
    ) -> Tuple[NDArray[Any], List[AnyAxis]]:
        """apply numpy.ndarray.squeeze while keeping track of the axis descriptions remaining"""
        if data.ndim != len(axes):
            raise ValueError(
                f"tensor shape {data.shape} does not match described axes"
                + f" {[a.id for a in axes]}"
            )

        axes = [deepcopy(a) for a, s in zip(axes, data.shape) if s != 1]
        return data.squeeze(), axes

    def normalize(
        data: NDArray[Any], axis: Optional[Tuple[int, ...]], eps: float = 1e-7
    ) -> NDArray[np.float32]:
        data = data.astype("float32")
        data -= data.min(axis=axis, keepdims=True)
        data /= data.max(axis=axis, keepdims=True) + eps
        return data

    def to_2d_image(data: NDArray[Any], axes: Sequence[AnyAxis]):
        original_shape = data.shape
        original_axes = list(axes)
        data, axes = squeeze(data, axes)

        # take slice fom any batch or index axis if needed
        # and convert the first channel axis and take a slice from any additional channel axes
        slices: Tuple[slice, ...] = ()
        ndim = data.ndim
        ndim_need = 3 if any(isinstance(a, ChannelAxis) for a in axes) else 2
        has_c_axis = False
        for i, a in enumerate(axes):
            s = data.shape[i]
            assert s > 1
            if (
                isinstance(a, (BatchAxis, IndexInputAxis, IndexOutputAxis))
                and ndim > ndim_need
            ):
                data = data[slices + (slice(s // 2 - 1, s // 2),)]
                ndim -= 1
            elif isinstance(a, ChannelAxis):
                if has_c_axis:
                    # second channel axis
                    data = data[slices + (slice(0, 1),)]
                    ndim -= 1
                else:
                    has_c_axis = True
                    if s == 2:
                        # visualize two channels with cyan and magenta
                        data = np.concatenate(
                            [
                                data[slices + (slice(1, 2),)],
                                data[slices + (slice(0, 1),)],
                                (
                                    data[slices + (slice(0, 1),)]
                                    + data[slices + (slice(1, 2),)]
                                )
                                / 2,  # TODO: take maximum instead?
                            ],
                            axis=i,
                        )
                    elif data.shape[i] == 3:
                        pass  # visualize 3 channels as RGB
                    else:
                        # visualize first 3 channels as RGB
                        data = data[slices + (slice(3),)]

                    assert data.shape[i] == 3

            slices += (slice(None),)

        data, axes = squeeze(data, axes)
        assert len(axes) == ndim
        # take slice from z axis if needed
        slices = ()
        if ndim > ndim_need:
            for i, a in enumerate(axes):
                s = data.shape[i]
                if a.id == AxisId("z"):
                    data = data[slices + (slice(s // 2 - 1, s // 2),)]
                    data, axes = squeeze(data, axes)
                    ndim -= 1
                    break

            slices += (slice(None),)

        # take slice from any space or time axis
        slices = ()

        for i, a in enumerate(axes):
            if ndim <= ndim_need:
                break

            s = data.shape[i]
            assert s > 1
            if isinstance(
                a, (SpaceInputAxis, SpaceOutputAxis, TimeInputAxis, TimeOutputAxis)
            ):
                data = data[slices + (slice(s // 2 - 1, s // 2),)]
                ndim -= 1

            slices += (slice(None),)

        del slices
        data, axes = squeeze(data, axes)
        assert len(axes) == ndim

        if (has_c_axis and ndim != 3) or (not has_c_axis and ndim != 2):
            raise ValueError(
                f"Failed to construct cover image from shape {original_shape} with axes {[a.id for a in original_axes]}."
            )

        if not has_c_axis:
            assert ndim == 2
            data = np.repeat(data[:, :, None], 3, axis=2)
            axes.append(ChannelAxis(channel_names=list(map(Identifier, "RGB"))))
            ndim += 1

        assert ndim == 3

        # transpose axis order such that longest axis comes first...
        axis_order: List[int] = list(np.argsort(list(data.shape)))
        axis_order.reverse()
        # ... and channel axis is last
        c = [i for i in range(3) if isinstance(axes[i], ChannelAxis)][0]
        axis_order.append(axis_order.pop(c))
        axes = [axes[ao] for ao in axis_order]
        data = data.transpose(axis_order)

        # h, w = data.shape[:2]
        # if h / w  in (1.0 or 2.0):
        #     pass
        # elif h / w < 2:
        # TODO: enforce 2:1 or 1:1 aspect ratio for generated cover images

        norm_along = (
            tuple(i for i, a in enumerate(axes) if a.type in ("space", "time")) or None
        )
        # normalize the data and map to 8 bit
        data = normalize(data, norm_along)
        data = (data * 255).astype("uint8")

        return data

    def create_diagonal_split_image(im0: NDArray[Any], im1: NDArray[Any]):
        assert im0.dtype == im1.dtype == np.uint8
        assert im0.shape == im1.shape
        assert im0.ndim == 3
        N, M, C = im0.shape
        assert C == 3
        out = np.ones((N, M, C), dtype="uint8")
        for c in range(C):
            outc = np.tril(im0[..., c])
            mask = outc == 0
            outc[mask] = np.triu(im1[..., c])[mask]
            out[..., c] = outc

        return out

    if not inputs:
        raise ValueError("Missing test input tensor for cover generation.")

    if not outputs:
        raise ValueError("Missing test output tensor for cover generation.")

    ipt_descr, ipt = inputs[0]
    out_descr, out = outputs[0]

    ipt_img = to_2d_image(ipt, ipt_descr.axes)
    out_img = to_2d_image(out, out_descr.axes)

    cover_folder = Path(mkdtemp())
    if ipt_img.shape == out_img.shape:
        covers = [cover_folder / "cover.png"]
        imwrite(covers[0], create_diagonal_split_image(ipt_img, out_img))
    else:
        covers = [cover_folder / "input.png", cover_folder / "output.png"]
        imwrite(covers[0], ipt_img)
        imwrite(covers[1], out_img)

    return covers
