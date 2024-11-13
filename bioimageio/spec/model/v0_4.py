from __future__ import annotations

import collections.abc
from typing import (
    Any,
    ClassVar,
    Dict,
    FrozenSet,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import numpy as np
from annotated_types import Ge, Interval, MaxLen, MinLen, MultipleOf
from numpy.typing import NDArray
from pydantic import (
    AllowInfNan,
    Discriminator,
    Field,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    TypeAdapter,
    ValidationInfo,
    WrapSerializer,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated, LiteralString, Self, assert_never

from .._internal.common_nodes import (
    KwargsNode,
    Node,
    NodeWithExplicitlySetFields,
    StringNode,
)
from .._internal.constants import SHA256_HINT
from .._internal.field_validation import validate_unique_entries
from .._internal.field_warning import issue_warning, warn
from .._internal.io import (
    BioimageioYamlContent,
    WithSuffix,
    download,
    include_in_package_serializer,
)
from .._internal.io import FileDescr as FileDescr
from .._internal.io_basics import AbsoluteFilePath as AbsoluteFilePath
from .._internal.io_basics import Sha256 as Sha256
from .._internal.io_utils import load_array
from .._internal.packaging_context import packaging_context_var
from .._internal.types import Datetime as Datetime
from .._internal.types import Identifier as Identifier
from .._internal.types import ImportantFileSource, LowerCaseIdentifier
from .._internal.types import LicenseId as LicenseId
from .._internal.types import NotEmpty as NotEmpty
from .._internal.url import HttpUrl as HttpUrl
from .._internal.validator_annotations import AfterValidator, RestrictCharacters
from .._internal.version_type import Version as Version
from .._internal.warning_levels import ALERT, INFO
from ..dataset.v0_2 import VALID_COVER_IMAGE_EXTENSIONS as VALID_COVER_IMAGE_EXTENSIONS
from ..dataset.v0_2 import DatasetDescr as DatasetDescr
from ..dataset.v0_2 import LinkedDataset as LinkedDataset
from ..generic.v0_2 import AttachmentsDescr as AttachmentsDescr
from ..generic.v0_2 import Author as Author
from ..generic.v0_2 import BadgeDescr as BadgeDescr
from ..generic.v0_2 import CiteEntry as CiteEntry
from ..generic.v0_2 import Doi as Doi
from ..generic.v0_2 import GenericModelDescrBase
from ..generic.v0_2 import LinkedResource as LinkedResource
from ..generic.v0_2 import Maintainer as Maintainer
from ..generic.v0_2 import OrcidId as OrcidId
from ..generic.v0_2 import RelativeFilePath as RelativeFilePath
from ..generic.v0_2 import ResourceId as ResourceId
from ..generic.v0_2 import Uploader as Uploader
from ._v0_4_converter import convert_from_older_format


class ModelId(ResourceId):
    pass


AxesStr = Annotated[
    str, RestrictCharacters("bitczyx"), AfterValidator(validate_unique_entries)
]
AxesInCZYX = Annotated[
    str, RestrictCharacters("czyx"), AfterValidator(validate_unique_entries)
]

PostprocessingName = Literal[
    "binarize",
    "clip",
    "scale_linear",
    "sigmoid",
    "zero_mean_unit_variance",
    "scale_range",
    "scale_mean_variance",
]
PreprocessingName = Literal[
    "binarize",
    "clip",
    "scale_linear",
    "sigmoid",
    "zero_mean_unit_variance",
    "scale_range",
]


class TensorName(LowerCaseIdentifier):
    pass


class CallableFromDepencency(StringNode):
    _pattern = r"^.+\..+$"
    _submodule_adapter = TypeAdapter(Identifier)

    module_name: str

    @field_validator("module_name", mode="after")
    def check_submodules(cls, module_name: str) -> str:
        for submod in module_name.split("."):
            _ = cls._submodule_adapter.validate_python(submod)

        return module_name

    callable_name: Identifier

    @classmethod
    def _get_data(cls, valid_string_data: str):
        *mods, callname = valid_string_data.split(".")
        return dict(module_name=".".join(mods), callable_name=callname)


class CallableFromFile(StringNode):
    _pattern = r"^.+:.+$"
    source_file: Annotated[
        Union[RelativeFilePath, HttpUrl],
        Field(union_mode="left_to_right"),
        include_in_package_serializer,
    ]
    """∈📦 Python module that implements `callable_name`"""
    callable_name: Identifier
    """The Python identifier of  """

    @classmethod
    def _get_data(cls, valid_string_data: str):
        *file_parts, callname = valid_string_data.split(":")
        return dict(source_file=":".join(file_parts), callable_name=callname)


CustomCallable = Annotated[
    Union[CallableFromFile, CallableFromDepencency], Field(union_mode="left_to_right")
]


class Dependencies(StringNode):
    _pattern = r"^.+:.+$"
    manager: Annotated[NotEmpty[str], Field(examples=["conda", "maven", "pip"])]
    """Dependency manager"""

    file: Annotated[
        ImportantFileSource,
        Field(examples=["environment.yaml", "pom.xml", "requirements.txt"]),
    ]
    """∈📦 Dependency file"""

    @classmethod
    def _get_data(cls, valid_string_data: str):
        manager, *file_parts = valid_string_data.split(":")
        return dict(manager=manager, file=":".join(file_parts))


WeightsFormat = Literal[
    "keras_hdf5",
    "onnx",
    "pytorch_state_dict",
    "tensorflow_js",
    "tensorflow_saved_model_bundle",
    "torchscript",
]


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


class WeightsEntryDescrBase(FileDescr):
    type: ClassVar[WeightsFormat]
    weights_format_name: ClassVar[str]  # human readable

    source: ImportantFileSource
    """∈📦 The weights file."""

    attachments: Annotated[
        Union[AttachmentsDescr, None],
        warn(None, "Weights entry depends on additional attachments.", ALERT),
    ] = None
    """Attachments that are specific to this weights entry."""

    authors: Union[List[Author], None] = None
    """Authors
    Either the person(s) that have trained this model resulting in the original weights file.
        (If this is the initial weights entry, i.e. it does not have a `parent`)
    Or the person(s) who have converted the weights to this weights format.
        (If this is a child weight, i.e. it has a `parent` field)
    """

    dependencies: Annotated[
        Optional[Dependencies],
        warn(
            None,
            "Custom dependencies ({value}) specified. Avoid this whenever possible "
            + "to allow execution in a wider range of software environments.",
        ),
        Field(
            examples=[
                "conda:environment.yaml",
                "maven:./pom.xml",
                "pip:./requirements.txt",
            ]
        ),
    ] = None
    """Dependency manager and dependency file, specified as `<dependency manager>:<relative file path>`."""

    parent: Annotated[
        Optional[WeightsFormat], Field(examples=["pytorch_state_dict"])
    ] = None
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
    tensorflow_version: Optional[Version] = None
    """TensorFlow version used to create these weights"""

    @field_validator("tensorflow_version", mode="after")
    @classmethod
    def _tfv(cls, value: Any):
        if value is None:
            issue_warning(
                "missing. Please specify the TensorFlow version"
                + " these weights were created with.",
                value=value,
                severity=ALERT,
                field="tensorflow_version",
            )
        return value


class OnnxWeightsDescr(WeightsEntryDescrBase):
    type = "onnx"
    weights_format_name: ClassVar[str] = "ONNX"
    opset_version: Optional[Annotated[int, Ge(7)]] = None
    """ONNX opset version"""

    @field_validator("opset_version", mode="after")
    @classmethod
    def _ov(cls, value: Any):
        if value is None:
            issue_warning(
                "Missing ONNX opset version (aka ONNX opset number). "
                + "Please specify the ONNX opset version these weights were created"
                + " with.",
                value=value,
                severity=ALERT,
                field="opset_version",
            )
        return value


class PytorchStateDictWeightsDescr(WeightsEntryDescrBase):
    type = "pytorch_state_dict"
    weights_format_name: ClassVar[str] = "Pytorch State Dict"
    architecture: CustomCallable = Field(
        examples=["my_function.py:MyNetworkClass", "my_module.submodule.get_my_model"]
    )
    """callable returning a torch.nn.Module instance.
    Local implementation: `<relative path to file>:<identifier of implementation within the file>`.
    Implementation in a dependency: `<dependency-package>.<[dependency-module]>.<identifier>`."""

    architecture_sha256: Annotated[
        Optional[Sha256],
        Field(
            description=(
                "The SHA256 of the architecture source file, if the architecture is not"
                " defined in a module listed in `dependencies`\n"
            )
            + SHA256_HINT,
        ),
    ] = None
    """The SHA256 of the architecture source file,
    if the architecture is not defined in a module listed in `dependencies`"""

    @model_validator(mode="after")
    def check_architecture_sha256(self) -> Self:
        if isinstance(self.architecture, CallableFromFile):
            if self.architecture_sha256 is None:
                raise ValueError(
                    "Missing required `architecture_sha256` for `architecture` with"
                    + " source file."
                )
        elif self.architecture_sha256 is not None:
            raise ValueError(
                "Got `architecture_sha256` for architecture that does not have a source"
                + " file."
            )

        return self

    kwargs: Dict[str, Any] = Field(default_factory=dict)
    """key word arguments for the `architecture` callable"""

    pytorch_version: Optional[Version] = None
    """Version of the PyTorch library used.
    If `depencencies` is specified it should include pytorch and the verison has to match.
    (`dependencies` overrules `pytorch_version`)"""

    @field_validator("pytorch_version", mode="after")
    @classmethod
    def _ptv(cls, value: Any):
        if value is None:
            issue_warning(
                "missing. Please specify the PyTorch version these"
                + " PyTorch state dict weights were created with.",
                value=value,
                severity=ALERT,
                field="pytorch_version",
            )
        return value


class TorchscriptWeightsDescr(WeightsEntryDescrBase):
    type = "torchscript"
    weights_format_name: ClassVar[str] = "TorchScript"
    pytorch_version: Optional[Version] = None
    """Version of the PyTorch library used."""

    @field_validator("pytorch_version", mode="after")
    @classmethod
    def _ptv(cls, value: Any):
        if value is None:
            issue_warning(
                "missing. Please specify the PyTorch version these"
                + " Torchscript weights were created with.",
                value=value,
                severity=ALERT,
                field="pytorch_version",
            )
        return value


class TensorflowJsWeightsDescr(WeightsEntryDescrBase):
    type = "tensorflow_js"
    weights_format_name: ClassVar[str] = "Tensorflow.js"
    tensorflow_version: Optional[Version] = None
    """Version of the TensorFlow library used."""

    @field_validator("tensorflow_version", mode="after")
    @classmethod
    def _tfv(cls, value: Any):
        if value is None:
            issue_warning(
                "missing. Please specify the TensorFlow version"
                + " these TensorflowJs weights were created with.",
                value=value,
                severity=ALERT,
                field="tensorflow_version",
            )
        return value

    source: ImportantFileSource
    """∈📦 The multi-file weights.
    All required files/folders should be a zip archive."""


class TensorflowSavedModelBundleWeightsDescr(WeightsEntryDescrBase):
    type = "tensorflow_saved_model_bundle"
    weights_format_name: ClassVar[str] = "Tensorflow Saved Model"
    tensorflow_version: Optional[Version] = None
    """Version of the TensorFlow library used."""

    @field_validator("tensorflow_version", mode="after")
    @classmethod
    def _tfv(cls, value: Any):
        if value is None:
            issue_warning(
                "missing. Please specify the TensorFlow version"
                + " these Tensorflow saved model bundle weights were created with.",
                value=value,
                severity=ALERT,
                field="tensorflow_version",
            )
        return value


class ParameterizedInputShape(Node):
    """A sequence of valid shapes given by `shape_k = min + k * step for k in {0, 1, ...}`."""

    min: NotEmpty[List[int]]
    """The minimum input shape"""

    step: NotEmpty[List[int]]
    """The minimum shape change"""

    def __len__(self) -> int:
        return len(self.min)

    @model_validator(mode="after")
    def matching_lengths(self) -> Self:
        if len(self.min) != len(self.step):
            raise ValueError("`min` and `step` required to have the same length")

        return self


class ImplicitOutputShape(Node):
    """Output tensor shape depending on an input tensor shape.
    `shape(output_tensor) = shape(input_tensor) * scale + 2 * offset`"""

    reference_tensor: TensorName
    """Name of the reference tensor."""

    scale: NotEmpty[List[Optional[float]]]
    """output_pix/input_pix for each dimension.
    'null' values indicate new dimensions, whose length is defined by 2*`offset`"""

    offset: NotEmpty[List[Union[int, Annotated[float, MultipleOf(0.5)]]]]
    """Position of origin wrt to input."""

    def __len__(self) -> int:
        return len(self.scale)

    @model_validator(mode="after")
    def matching_lengths(self) -> Self:
        if len(self.scale) != len(self.offset):
            raise ValueError(
                f"scale {self.scale} has to have same length as offset {self.offset}!"
            )
        # if we have an expanded dimension, make sure that it's offet is not zero
        for sc, off in zip(self.scale, self.offset):
            if sc is None and not off:
                raise ValueError("`offset` must not be zero if `scale` is none/zero")

        return self


class TensorDescrBase(Node):
    name: TensorName
    """Tensor name. No duplicates are allowed."""

    description: str = ""

    axes: AxesStr
    """Axes identifying characters. Same length and order as the axes in `shape`.
    | axis | description |
    | --- | --- |
    |  b  |  batch (groups multiple samples) |
    |  i  |  instance/index/element |
    |  t  |  time |
    |  c  |  channel |
    |  z  |  spatial dimension z |
    |  y  |  spatial dimension y |
    |  x  |  spatial dimension x |
    """

    data_range: Optional[
        Tuple[Annotated[float, AllowInfNan(True)], Annotated[float, AllowInfNan(True)]]
    ] = None
    """Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
    If not specified, the full data range that can be expressed in `data_type` is allowed."""


class ProcessingKwargs(KwargsNode):
    """base class for pre-/postprocessing key word arguments"""


class ProcessingDescrBase(NodeWithExplicitlySetFields):
    """processing base class"""

    # name: Literal[PreprocessingName, PostprocessingName]  # todo: make abstract field
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset({"name"})


class BinarizeKwargs(ProcessingKwargs):
    """key word arguments for `BinarizeDescr`"""

    threshold: float
    """The fixed threshold"""


class BinarizeDescr(ProcessingDescrBase):
    """BinarizeDescr the tensor with a fixed `BinarizeKwargs.threshold`.
    Values above the threshold will be set to one, values below the threshold to zero.
    """

    name: Literal["binarize"] = "binarize"
    kwargs: BinarizeKwargs


class ClipKwargs(ProcessingKwargs):
    """key word arguments for `ClipDescr`"""

    min: float
    """minimum value for clipping"""
    max: float
    """maximum value for clipping"""


class ClipDescr(ProcessingDescrBase):
    """Clip tensor values to a range.

    Set tensor values below `ClipKwargs.min` to `ClipKwargs.min`
    and above `ClipKwargs.max` to `ClipKwargs.max`.
    """

    name: Literal["clip"] = "clip"

    kwargs: ClipKwargs


class ScaleLinearKwargs(ProcessingKwargs):
    """key word arguments for `ScaleLinearDescr`"""

    axes: Annotated[Optional[AxesInCZYX], Field(examples=["xy"])] = None
    """The subset of axes to scale jointly.
    For example xy to scale the two image axes for 2d data jointly."""

    gain: Union[float, List[float]] = 1.0
    """multiplicative factor"""

    offset: Union[float, List[float]] = 0.0
    """additive term"""

    @model_validator(mode="after")
    def either_gain_or_offset(self) -> Self:
        if (
            self.gain == 1.0
            or isinstance(self.gain, list)
            and all(g == 1.0 for g in self.gain)
        ) and (
            self.offset == 0.0
            or isinstance(self.offset, list)
            and all(off == 0.0 for off in self.offset)
        ):
            raise ValueError(
                "Redunt linear scaling not allowd. Set `gain` != 1.0 and/or `offset` !="
                + " 0.0."
            )

        return self


class ScaleLinearDescr(ProcessingDescrBase):
    """Fixed linear scaling."""

    name: Literal["scale_linear"] = "scale_linear"
    kwargs: ScaleLinearKwargs


class SigmoidDescr(ProcessingDescrBase):
    """The logistic sigmoid funciton, a.k.a. expit function."""

    name: Literal["sigmoid"] = "sigmoid"

    @property
    def kwargs(self) -> ProcessingKwargs:
        """empty kwargs"""
        return ProcessingKwargs()


class ZeroMeanUnitVarianceKwargs(ProcessingKwargs):
    """key word arguments for `ZeroMeanUnitVarianceDescr`"""

    mode: Literal["fixed", "per_dataset", "per_sample"] = "fixed"
    """Mode for computing mean and variance.
    |     mode    |             description              |
    | ----------- | ------------------------------------ |
    |   fixed     | Fixed values for mean and variance   |
    | per_dataset | Compute for the entire dataset       |
    | per_sample  | Compute for each sample individually |
    """
    axes: Annotated[AxesInCZYX, Field(examples=["xy"])]
    """The subset of axes to normalize jointly.
    For example `xy` to normalize the two image axes for 2d data jointly."""

    mean: Annotated[
        Union[float, NotEmpty[List[float]], None], Field(examples=[(1.1, 2.2, 3.3)])
    ] = None
    """The mean value(s) to use for `mode: fixed`.
    For example `[1.1, 2.2, 3.3]` in the case of a 3 channel image with `axes: xy`."""
    # todo: check if means match input axes (for mode 'fixed')

    std: Annotated[
        Union[float, NotEmpty[List[float]], None], Field(examples=[(0.1, 0.2, 0.3)])
    ] = None
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


class ZeroMeanUnitVarianceDescr(ProcessingDescrBase):
    """Subtract mean and divide by variance."""

    name: Literal["zero_mean_unit_variance"] = "zero_mean_unit_variance"
    kwargs: ZeroMeanUnitVarianceKwargs


class ScaleRangeKwargs(ProcessingKwargs):
    """key word arguments for `ScaleRangeDescr`

    For `min_percentile`=0.0 (the default) and `max_percentile`=100 (the default)
    this processing step normalizes data to the [0, 1] intervall.
    For other percentiles the normalized values will partially be outside the [0, 1]
    intervall. Use `ScaleRange` followed by `ClipDescr` if you want to limit the
    normalized values to a range.
    """

    mode: Literal["per_dataset", "per_sample"]
    """Mode for computing percentiles.
    |     mode    |             description              |
    | ----------- | ------------------------------------ |
    | per_dataset | compute for the entire dataset       |
    | per_sample  | compute for each sample individually |
    """
    axes: Annotated[AxesInCZYX, Field(examples=["xy"])]
    """The subset of axes to normalize jointly.
    For example xy to normalize the two image axes for 2d data jointly."""

    min_percentile: Annotated[Union[int, float], Interval(ge=0, lt=100)] = 0.0
    """The lower percentile used to determine the value to align with zero."""

    max_percentile: Annotated[Union[int, float], Interval(gt=1, le=100)] = 100.0
    """The upper percentile used to determine the value to align with one.
    Has to be bigger than `min_percentile`.
    The range is 1 to 100 instead of 0 to 100 to avoid mistakenly
    accepting percentiles specified in the range 0.0 to 1.0."""

    @model_validator(mode="after")
    def min_smaller_max(self, info: ValidationInfo) -> Self:
        if self.min_percentile >= self.max_percentile:
            raise ValueError(
                f"min_percentile {self.min_percentile} >= max_percentile"
                + f" {self.max_percentile}"
            )

        return self

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """Epsilon for numeric stability.
    `out = (tensor - v_lower) / (v_upper - v_lower + eps)`;
    with `v_lower,v_upper` values at the respective percentiles."""

    reference_tensor: Optional[TensorName] = None
    """Tensor name to compute the percentiles from. Default: The tensor itself.
    For any tensor in `inputs` only input tensor references are allowed.
    For a tensor in `outputs` only input tensor refereences are allowed if `mode: per_dataset`"""


class ScaleRangeDescr(ProcessingDescrBase):
    """Scale with percentiles."""

    name: Literal["scale_range"] = "scale_range"
    kwargs: ScaleRangeKwargs


class ScaleMeanVarianceKwargs(ProcessingKwargs):
    """key word arguments for `ScaleMeanVarianceDescr`"""

    mode: Literal["per_dataset", "per_sample"]
    """Mode for computing mean and variance.
    |     mode    |             description              |
    | ----------- | ------------------------------------ |
    | per_dataset | Compute for the entire dataset       |
    | per_sample  | Compute for each sample individually |
    """

    reference_tensor: TensorName
    """Name of tensor to match."""

    axes: Annotated[Optional[AxesInCZYX], Field(examples=["xy"])] = None
    """The subset of axes to scale jointly.
    For example xy to normalize the two image axes for 2d data jointly.
    Default: scale all non-batch axes jointly."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """Epsilon for numeric stability:
    "`out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean."""


class ScaleMeanVarianceDescr(ProcessingDescrBase):
    """Scale the tensor s.t. its mean and variance match a reference tensor."""

    name: Literal["scale_mean_variance"] = "scale_mean_variance"
    kwargs: ScaleMeanVarianceKwargs


PreprocessingDescr = Annotated[
    Union[
        BinarizeDescr,
        ClipDescr,
        ScaleLinearDescr,
        SigmoidDescr,
        ZeroMeanUnitVarianceDescr,
        ScaleRangeDescr,
    ],
    Discriminator("name"),
]
PostprocessingDescr = Annotated[
    Union[
        BinarizeDescr,
        ClipDescr,
        ScaleLinearDescr,
        SigmoidDescr,
        ZeroMeanUnitVarianceDescr,
        ScaleRangeDescr,
        ScaleMeanVarianceDescr,
    ],
    Discriminator("name"),
]


class InputTensorDescr(TensorDescrBase):
    data_type: Literal["float32", "uint8", "uint16"]
    """For now an input tensor is expected to be given as `float32`.
    The data flow in bioimage.io models is explained
    [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit)."""

    shape: Annotated[
        Union[Sequence[int], ParameterizedInputShape],
        Field(
            examples=[(1, 512, 512, 1), dict(min=(1, 64, 64, 1), step=(0, 32, 32, 0))]
        ),
    ]
    """Specification of input tensor shape."""

    preprocessing: List[PreprocessingDescr] = Field(default_factory=list)
    """Description of how this input should be preprocessed."""

    @model_validator(mode="after")
    def zero_batch_step_and_one_batch_size(self) -> Self:
        bidx = self.axes.find("b")
        if bidx == -1:
            return self

        if isinstance(self.shape, ParameterizedInputShape):
            step = self.shape.step
            shape = self.shape.min
            if step[bidx] != 0:
                raise ValueError(
                    "Input shape step has to be zero in the batch dimension (the batch"
                    + " dimension can always be increased, but `step` should specify how"
                    + " to increase the minimal shape to find the largest single batch"
                    + " shape)"
                )
        else:
            shape = self.shape

        if shape[bidx] != 1:
            raise ValueError("Input shape has to be 1 in the batch dimension b.")

        return self

    @model_validator(mode="after")
    def validate_preprocessing_kwargs(self) -> Self:
        for p in self.preprocessing:
            kwargs_axes = p.kwargs.get("axes", "")
            if not isinstance(kwargs_axes, str):
                raise ValueError(
                    f"Expected an `axes` string, but got {type(kwargs_axes)}"
                )

            if any(a not in self.axes for a in kwargs_axes):
                raise ValueError("`kwargs.axes` needs to be subset of `axes`")

        return self


class OutputTensorDescr(TensorDescrBase):
    data_type: Literal[
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
    """Data type.
    The data flow in bioimage.io models is explained
    [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit)."""

    shape: Union[Sequence[int], ImplicitOutputShape]
    """Output tensor shape."""

    halo: Optional[Sequence[int]] = None
    """The `halo` that should be cropped from the output tensor to avoid boundary effects.
    The `halo` is to be cropped from both sides, i.e. `shape_after_crop = shape - 2 * halo`.
    To document a `halo` that is already cropped by the model `shape.offset` has to be used instead."""

    postprocessing: List[PostprocessingDescr] = Field(default_factory=list)
    """Description of how this output should be postprocessed."""

    @model_validator(mode="after")
    def matching_halo_length(self) -> Self:
        if self.halo and len(self.halo) != len(self.shape):
            raise ValueError(
                f"halo {self.halo} has to have same length as shape {self.shape}!"
            )

        return self

    @model_validator(mode="after")
    def validate_postprocessing_kwargs(self) -> Self:
        for p in self.postprocessing:
            kwargs_axes = p.kwargs.get("axes", "")
            if not isinstance(kwargs_axes, str):
                raise ValueError(f"Expected {kwargs_axes} to be a string")

            if any(a not in self.axes for a in kwargs_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes")

        return self


KnownRunMode = Literal["deepimagej"]


class RunMode(Node):
    name: Annotated[
        Union[KnownRunMode, str], warn(KnownRunMode, "Unknown run mode '{value}'.")
    ]
    """Run mode name"""

    kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Run mode specific key word arguments"""


class LinkedModel(Node):
    """Reference to a bioimage.io model."""

    id: ModelId
    """A valid model `id` from the bioimage.io collection."""

    version_number: Optional[int] = None
    """version number (n-th published version, not the semantic version) of linked model"""


def package_weights(
    value: Node,  # Union[v0_4.WeightsDescr, v0_5.WeightsDescr]
    handler: SerializerFunctionWrapHandler,
    info: SerializationInfo,
):
    ctxt = packaging_context_var.get()
    if ctxt is not None and ctxt.weights_priority_order is not None:
        for wf in ctxt.weights_priority_order:
            w = getattr(value, wf, None)
            if w is not None:
                break
        else:
            raise ValueError(
                "None of the weight formats in `weights_priority_order`"
                + f" ({ctxt.weights_priority_order}) is present in the given model."
            )

        assert isinstance(w, Node), type(w)
        # construct WeightsDescr with new single weight format entry
        new_w = w.model_construct(**{k: v for k, v in w if k != "parent"})
        value = value.model_construct(None, **{wf: new_w})

    return handler(
        value, info  # pyright: ignore[reportArgumentType]  # taken from pydantic docs
    )


class ModelDescr(GenericModelDescrBase, title="bioimage.io model specification"):
    """Specification of the fields used in a bioimage.io-compliant RDF that describes AI models with pretrained weights.

    These fields are typically stored in a YAML file which we call a model resource description file (model RDF).
    """

    format_version: Literal["0.4.10",] = "0.4.10"
    """Version of the bioimage.io model description specification used.
    When creating a new model always use the latest micro/patch version described here.
    The `format_version` is important for any consumer software to understand how to parse the fields.
    """

    type: Literal["model"] = "model"
    """Specialized resource type 'model'"""

    id: Optional[ModelId] = None
    """bioimage.io-wide unique resource identifier
    assigned by bioimage.io; version **un**specific."""

    authors: NotEmpty[  # pyright: ignore[reportGeneralTypeIssues]  # make mandatory
        List[Author]
    ]
    """The authors are the creators of the model RDF and the primary points of contact."""

    documentation: Annotated[
        ImportantFileSource,
        Field(
            examples=[
                "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md",
                "README.md",
            ],
        ),
    ]
    """∈📦 URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
    The documentation should include a '[#[#]]# Validation' (sub)section
    with details on how to quantitatively validate the model on unseen data."""

    inputs: NotEmpty[List[InputTensorDescr]]
    """Describes the input tensors expected by this model."""

    license: Annotated[
        Union[LicenseId, str],
        warn(LicenseId, "Unknown license id '{value}'."),
        Field(examples=["CC0-1.0", "MIT", "BSD-2-Clause"]),
    ]
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do notsupport custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose
    ) to discuss your intentions with the community."""

    name: Annotated[
        str,
        MinLen(1),
        warn(MinLen(5), "Name shorter than 5 characters.", INFO),
        warn(MaxLen(64), "Name longer than 64 characters.", INFO),
    ]
    """A human-readable name of this model.
    It should be no longer than 64 characters and only contain letter, number, underscore, minus or space characters."""

    outputs: NotEmpty[List[OutputTensorDescr]]
    """Describes the output tensors."""

    @field_validator("inputs", "outputs")
    @classmethod
    def unique_tensor_descr_names(
        cls, value: Sequence[Union[InputTensorDescr, OutputTensorDescr]]
    ) -> Sequence[Union[InputTensorDescr, OutputTensorDescr]]:
        unique_names = {str(v.name) for v in value}
        if len(unique_names) != len(value):
            raise ValueError("Duplicate tensor descriptor names")

        return value

    @model_validator(mode="after")
    def unique_io_names(self) -> Self:
        unique_names = {str(ss.name) for s in (self.inputs, self.outputs) for ss in s}
        if len(unique_names) != (len(self.inputs) + len(self.outputs)):
            raise ValueError("Duplicate tensor descriptor names across inputs/outputs")

        return self

    @model_validator(mode="after")
    def minimum_shape2valid_output(self) -> Self:
        tensors_by_name: Dict[
            TensorName, Union[InputTensorDescr, OutputTensorDescr]
        ] = {t.name: t for t in self.inputs + self.outputs}

        for out in self.outputs:
            if isinstance(out.shape, ImplicitOutputShape):
                ndim_ref = len(tensors_by_name[out.shape.reference_tensor].shape)
                ndim_out_ref = len(
                    [scale for scale in out.shape.scale if scale is not None]
                )
                if ndim_ref != ndim_out_ref:
                    expanded_dim_note = (
                        " Note that expanded dimensions (`scale`: null) are not"
                        + f" counted for {out.name}'sdimensionality here."
                        if None in out.shape.scale
                        else ""
                    )
                    raise ValueError(
                        f"Referenced tensor '{out.shape.reference_tensor}' with"
                        + f" {ndim_ref} dimensions does not match output tensor"
                        + f" '{out.name}' with"
                        + f" {ndim_out_ref} dimensions.{expanded_dim_note}"
                    )

            min_out_shape = self._get_min_shape(out, tensors_by_name)
            if out.halo:
                halo = out.halo
                halo_msg = f" for halo {out.halo}"
            else:
                halo = [0] * len(min_out_shape)
                halo_msg = ""

            if any([s - 2 * h < 1 for s, h in zip(min_out_shape, halo)]):
                raise ValueError(
                    f"Minimal shape {min_out_shape} of output {out.name} is too"
                    + f" small{halo_msg}."
                )

        return self

    @classmethod
    def _get_min_shape(
        cls,
        t: Union[InputTensorDescr, OutputTensorDescr],
        tensors_by_name: Dict[TensorName, Union[InputTensorDescr, OutputTensorDescr]],
    ) -> Sequence[int]:
        """output with subtracted halo has to result in meaningful output even for the minimal input
        see https://github.com/bioimage-io/spec-bioimage-io/issues/392
        """
        if isinstance(t.shape, collections.abc.Sequence):
            return t.shape
        elif isinstance(t.shape, ParameterizedInputShape):
            return t.shape.min
        elif isinstance(t.shape, ImplicitOutputShape):
            pass
        else:
            assert_never(t.shape)

        ref_shape = cls._get_min_shape(
            tensors_by_name[t.shape.reference_tensor], tensors_by_name
        )

        if None not in t.shape.scale:
            scale: Sequence[float, ...] = t.shape.scale  # type: ignore
        else:
            expanded_dims = [idx for idx, sc in enumerate(t.shape.scale) if sc is None]
            new_ref_shape: List[int] = []
            for idx in range(len(t.shape.scale)):
                ref_idx = idx - sum(int(exp < idx) for exp in expanded_dims)
                new_ref_shape.append(1 if idx in expanded_dims else ref_shape[ref_idx])

            ref_shape = new_ref_shape
            assert len(ref_shape) == len(t.shape.scale)
            scale = [0.0 if sc is None else sc for sc in t.shape.scale]

        offset = t.shape.offset
        assert len(offset) == len(scale)
        return [int(rs * s + 2 * off) for rs, s, off in zip(ref_shape, scale, offset)]

    @model_validator(mode="after")
    def validate_tensor_references_in_inputs(self) -> Self:
        for t in self.inputs:
            for proc in t.preprocessing:
                if "reference_tensor" not in proc.kwargs:
                    continue

                ref_tensor = proc.kwargs["reference_tensor"]
                if ref_tensor is not None and str(ref_tensor) not in {
                    str(t.name) for t in self.inputs
                }:
                    raise ValueError(f"'{ref_tensor}' not found in inputs")

                if ref_tensor == t.name:
                    raise ValueError(
                        f"invalid self reference for preprocessing of tensor {t.name}"
                    )

        return self

    @model_validator(mode="after")
    def validate_tensor_references_in_outputs(self) -> Self:
        for t in self.outputs:
            for proc in t.postprocessing:
                if "reference_tensor" not in proc.kwargs:
                    continue
                ref_tensor = proc.kwargs["reference_tensor"]
                if ref_tensor is not None and str(ref_tensor) not in {
                    str(t.name) for t in self.inputs
                }:
                    raise ValueError(f"{ref_tensor} not found in inputs")

        return self

    packaged_by: List[Author] = Field(default_factory=list)
    """The persons that have packaged and uploaded this model.
    Only required if those persons differ from the `authors`."""

    parent: Optional[LinkedModel] = None
    """The model from which this model is derived, e.g. by fine-tuning the weights."""

    @field_validator("parent", mode="before")
    @classmethod
    def ignore_url_parent(cls, parent: Any):
        if isinstance(parent, dict):
            return None

        else:
            return parent

    run_mode: Optional[RunMode] = None
    """Custom run mode for this model: for more complex prediction procedures like test time
    data augmentation that currently cannot be expressed in the specification.
    No standard run modes are defined yet."""

    sample_inputs: List[ImportantFileSource] = Field(default_factory=list)
    """∈📦 URLs/relative paths to sample inputs to illustrate possible inputs for the model,
    for example stored as PNG or TIFF images.
    The sample files primarily serve to inform a human user about an example use case"""

    sample_outputs: List[ImportantFileSource] = Field(default_factory=list)
    """∈📦 URLs/relative paths to sample outputs corresponding to the `sample_inputs`."""

    test_inputs: NotEmpty[
        List[Annotated[ImportantFileSource, WithSuffix(".npy", case_sensitive=True)]]
    ]
    """∈📦 Test input tensors compatible with the `inputs` description for a **single test case**.
    This means if your model has more than one input, you should provide one URL/relative path for each input.
    Each test input should be a file with an ndarray in
    [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
    The extension must be '.npy'."""

    test_outputs: NotEmpty[
        List[Annotated[ImportantFileSource, WithSuffix(".npy", case_sensitive=True)]]
    ]
    """∈📦 Analog to `test_inputs`."""

    timestamp: Datetime
    """Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
    with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."""

    training_data: Union[LinkedDataset, DatasetDescr, None] = None
    """The dataset used to train this model"""

    weights: Annotated[WeightsDescr, WrapSerializer(package_weights)]
    """The weights for this model.
    Weights can be given for different formats, but should otherwise be equivalent.
    The available weight formats determine which consumers can use this model."""

    @model_validator(mode="before")
    @classmethod
    def _convert_from_older_format(
        cls, data: BioimageioYamlContent, /
    ) -> BioimageioYamlContent:
        convert_from_older_format(data)
        return data

    def get_input_test_arrays(self) -> List[NDArray[Any]]:
        data = [load_array(download(ipt).path) for ipt in self.test_inputs]
        assert all(isinstance(d, np.ndarray) for d in data)
        return data

    def get_output_test_arrays(self) -> List[NDArray[Any]]:
        data = [load_array(download(out).path) for out in self.test_outputs]
        assert all(isinstance(d, np.ndarray) for d in data)
        return data
