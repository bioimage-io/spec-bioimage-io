from __future__ import annotations

from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from annotated_types import Ge, Interval, MaxLen, MultipleOf
from pydantic import (
    AllowInfNan,
    ConfigDict,
    FieldValidationInfo,
    HttpUrl,
    TypeAdapter,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated

from bioimageio.spec._internal._constants import SHA256_HINT
from bioimageio.spec._internal._utils import Field
from bioimageio.spec._internal._validate import WithSuffix
from bioimageio.spec._internal._warn import ALERT, INFO, warn
from bioimageio.spec.dataset.v0_2 import Dataset, LinkedDataset
from bioimageio.spec.generic.v0_2 import (
    Attachments,
    Author,
    GenericBaseNoSource,
    LinkedResource,
)
from bioimageio.spec.model.v0_3_converter import convert_model_from_v0_3_to_0_4_0
from bioimageio.spec.shared.nodes import FrozenDictNode, Kwargs, Node, StringNode
from bioimageio.spec.shared.types import (
    AxesInCZYX,
    AxesStr,
    CapitalStr,
    Datetime,
    FileSource,
    Identifier,
    LicenseId,
    NonEmpty,
    RawDict,
    RawMapping,
    RelativeFilePath,
    Sha256,
    Version,
)

Framework = Literal["pytorch", "tensorflow"]
Language = Literal["python", "java"]
PostprocessingName = Literal[
    "binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range", "scale_mean_variance"
]
PreprocessingName = Literal["binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range"]


class CallableFromDepencency(StringNode):
    _pattern = r"^.+\..+$"
    module_name: NonEmpty[str]
    callable_name: NonEmpty[str]

    @classmethod
    def _get_data(cls, valid_string_data: str):
        *mods, callname = valid_string_data.split(".")
        return dict(module_name=".".join(mods), callable_name=callname)


class CallableFromSourceFile(StringNode):
    _pattern = r"^.+:.+$"
    source_file: Union[HttpUrl, RelativeFilePath] = Field(in_package=True)
    callable_name: str

    @classmethod
    def _get_data(cls, valid_string_data: str):
        *file_parts, callname = valid_string_data.split(":")
        return dict(source_file=":".join(file_parts), callable_name=callname)


CustomCallable = Union[CallableFromSourceFile, CallableFromDepencency]


class Dependencies(StringNode):
    _pattern = r"^.+:.+$"
    manager: NonEmpty[str] = Field(examples=["conda", "maven", "pip"])
    """Dependency manager"""

    file: Union[HttpUrl, RelativeFilePath] = Field(
        in_package=True, examples=["environment.yaml", "pom.xml", "requirements.txt"]
    )
    """Dependency file"""

    @classmethod
    def _get_data(cls, valid_string_data: str):
        manager, *file_parts = valid_string_data.split(":")
        return dict(manager=manager, file=":".join(file_parts))


WeightsFormat = Literal[
    "keras_hdf5", "onnx", "pytorch_state_dict", "tensorflow_js", "tensorflow_saved_model_bundle", "torchscript"
]


class Weights(Node):
    keras_hdf5: Optional[KerasHdf5Entry] = None
    onnx: Optional[OnnxEntry] = None
    pytorch_state_dict: Optional[PytorchStateDictEntry] = None
    tensorflow_js: Optional[TensorflowJsEntry] = None
    tensorflow_saved_model_bundle: Optional[TensorflowSavedModelBundleEntry] = None
    torchscript: Optional[TorchscriptEntry] = None

    @model_validator(mode="after")
    def check_one_entry(self):
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


class WeightsEntryBase(Node):
    model_config = {**Node.model_config, "exclude": ("type",)}
    weights_format_name: ClassVar[str]  # human readable

    source: FileSource = Field(in_package=True)
    """The weights file."""

    sha256: Annotated[Union[Sha256, None], warn(Sha256)] = Field(
        None, description="SHA256 checksum of the source file\n" + SHA256_HINT
    )
    """SHA256 checksum of the source file"""

    attachments: Annotated[Union[Attachments, None], warn(None, ALERT)] = None
    """Attachments that are specific to this weights entry."""

    authors: Union[Tuple[Author, ...], None] = None
    """Authors:
    If this is the initial weights entry (in other words: it does not have a `parent` field):
        the person(s) that have trained this model.
    If this is a child weight (it has a `parent` field):
        the person(s) who have converted the weights to this format.
    """

    dependencies: Annotated[Optional[Dependencies], warn(None, ALERT)] = Field(
        None, examples=["conda:environment.yaml", "maven:./pom.xml", "pip:./requirements.txt"]
    )
    """"Dependency manager and dependency file, specified as `<dependency manager>:<relative file path>`."""

    parent: Optional[WeightsFormat] = Field(None, examples=["pytorch_state_dict"])
    """The source weights these weights were converted from.
    For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
    The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
    All weight entries except one (the initial set of weights resulting from training the model),
    need to have this field."""
    # todo: validate


class KerasHdf5Entry(WeightsEntryBase):
    type: Literal["keras_hdf5"] = Field("keras_hdf5", exclude=True)
    weights_format_name: ClassVar[str] = "Keras HDF5"
    tensorflow_version: Annotated[Union[Version, None], warn(Version, ALERT)] = None
    """TensorFlow version used to create these weights"""


class OnnxEntry(WeightsEntryBase):
    type: Literal["onnx"] = Field("onnx", exclude=True)
    weights_format_name: ClassVar[str] = "ONNX"
    opset_version: Annotated[Union[Annotated[int, Ge(7)], None], warn(int, ALERT)] = None
    """ONNX opset version"""


class PytorchStateDictEntry(WeightsEntryBase):
    type: Literal["pytorch_state_dict"] = Field("pytorch_state_dict", exclude=True)
    weights_format_name: ClassVar[str] = "Pytorch State Dict"
    architecture: CustomCallable = Field(examples=["my_function.py:MyNetworkClass", "my_module.submodule.get_my_model"])
    """callable returning a torch.nn.Module instance.
    Local implementation: `<relative path to file>:<identifier of implementation within the file>`.
    Implementation in a dependency: `<dependency-package>.<[dependency-module]>.<identifier>`."""

    # todo: include in `architecture` field
    architecture_sha256: Union[Sha256, None] = Field(
        None,
        description=(
            "The SHA256 of the architecture source file, "
            "if the architecture is not defined in a module listed in `dependencies`\n"
        )
        + SHA256_HINT,
    )
    """The SHA256 of the architecture source file,
    if the architecture is not defined in a module listed in `dependencies`"""

    @model_validator(mode="after")
    def check_architecture_sha256(self):
        if isinstance(self.architecture, CallableFromSourceFile):
            if self.architecture_sha256 is None:
                raise ValueError("Missing required `architecture_sha256` for `architecture` with source file.")
        elif self.architecture_sha256 is not None:
            raise ValueError("Got `architecture_sha256` for architecture that does not have a source file.")

        return self

    kwargs: FrozenDictNode[NonEmpty[str], Any] = Field(default_factory=dict)
    """key word arguments for the `architecture` callable"""

    pytorch_version: Annotated[Union[Version, None], warn(Version)] = None
    """Version of the PyTorch library used.
    If `depencencies` is specified it should include pytorch and the verison has to match.
    (`dependencies` overrules `pytorch_version`)"""


class TorchscriptEntry(WeightsEntryBase):
    type: Literal["torchscript"] = Field("torchscript", exclude=True)
    weights_format_name: ClassVar[str] = "TorchScript"
    pytorch_version: Annotated[Union[Version, None], warn(Version)] = None
    """Version of the PyTorch library used."""


class TensorflowJsEntry(WeightsEntryBase):
    type: Literal["tensorflow_js"] = Field("tensorflow_js", exclude=True)
    weights_format_name: ClassVar[str] = "Tensorflow.js"
    tensorflow_version: Annotated[Union[Version, None], warn(Version)] = None
    """Version of the TensorFlow library used."""

    source: Union[HttpUrl, RelativeFilePath] = Field(in_package=True)
    """The multi-file weights.
    All required files/folders should be a zip archive."""


class TensorflowSavedModelBundleEntry(WeightsEntryBase):
    type: Literal["tensorflow_saved_model_bundle"] = Field("tensorflow_saved_model_bundle", exclude=True)
    weights_format_name: ClassVar[str] = "Tensorflow Saved Model"
    tensorflow_version: Annotated[Union[Version, None], warn(Version)] = None
    """Version of the TensorFlow library used."""


WeightsEntry = Annotated[
    Union[
        KerasHdf5Entry,
        OnnxEntry,
        TorchscriptEntry,
        PytorchStateDictEntry,
        TensorflowJsEntry,
        TensorflowSavedModelBundleEntry,
    ],
    Field(discriminator="type"),
]


class ParametrizedInputShape(Node):
    """A sequence of valid shapes given by `shape_k = min + k * step for k in {0, 1, ...}`."""

    min: NonEmpty[Tuple[int, ...]]
    """The minimum input shape"""

    step: NonEmpty[Tuple[int, ...]]
    """The minimum shape change"""

    def __len__(self) -> int:
        return len(self.min)

    @model_validator(mode="after")
    def matching_lengths(self):
        if len(self.min) != len(self.step):
            raise ValueError("`min` and `step` required to have the same length")

        return self


class ImplicitOutputShape(Node):
    """Output tensor shape depending on an input tensor shape.
    `shape(output_tensor) = shape(input_tensor) * scale + 2 * offset`"""

    reference_tensor: NonEmpty[str]
    """Name of the reference tensor."""

    scale: NonEmpty[Tuple[Union[float, None], ...]]
    """output_pix/input_pix for each dimension.
    'null' values indicate new dimensions, whose length is defined by 2*`offset`"""

    offset: NonEmpty[Tuple[Annotated[float, MultipleOf(0.5)], ...]]
    """Position of origin wrt to input."""

    def __len__(self) -> int:
        return len(self.scale)

    @model_validator(mode="after")
    def matching_lengths(self):
        if len(self.scale) != len(self.offset):
            raise ValueError(f"scale {self.scale} has to have same length as offset {self.offset}!")
        # if we have an expanded dimension, make sure that it's offet is not zero
        for sc, off in zip(self.scale, self.offset):
            if sc is None and not off:
                raise ValueError("`offset` must not be zero if `scale` is none/zero")

        return self


class TensorBase(Node):
    name: Identifier  # todo: validate duplicates
    """Tensor name. No duplicates are allowed."""

    description: str = ""
    """Brief descripiton of the tensor"""

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

    data_type: str
    """The data type of this tensor."""

    data_range: Optional[Tuple[Annotated[float, AllowInfNan(True)], Annotated[float, AllowInfNan(True)]]] = None
    """Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
    If not specified, the full data range that can be expressed in `data_type` is allowed."""


_MODE_DESCR_WO_FIXED = """Mode for computing mean and variance.
| mode | description |
| --- | ---- |
| per_dataset | mean and variance are computed for the entire dataset |
| per_sample | mean and variance are computed for each sample individually |
"""

_MODE_DESCR = (
    _MODE_DESCR_WO_FIXED
    + """
| fixed | fixed values for mean and variance |
"""
)


class ProcessingKwargs(Kwargs):
    """base class for pre-/postprocessing key word arguments"""

    # mode: Literal["fixed", "per_dataset", "per_sample"] = "fixed"


class Processing(Node):  # todo: add ABC
    """abstract processing base class"""

    name: Literal[PreprocessingName, PostprocessingName]

    @model_validator(mode="before")
    @classmethod
    def check_name_given_for_raw_input(cls, data: Union[Processing, RawMapping]) -> Union[Processing, RawMapping]:
        if not isinstance(data, Processing) and "name" not in data:
            raise AssertionError("'name' field mandatory for raw data input.")

        return data

    kwargs: ProcessingKwargs = ProcessingKwargs()
    """key word arguments"""


class BinarizeKwargs(ProcessingKwargs):
    threshold: float
    """The fixed threshold"""


class Binarize(Processing):
    """Binarize the tensor with a fixed threshold.
    Values above the threshold will be set to one, values below the threshold to zero."""

    name: Literal["binarize"] = "binarize"
    kwargs: BinarizeKwargs


class ClipKwargs(ProcessingKwargs):
    min: float
    """minimum value for clipping"""
    max: float
    """maximum value for clipping"""


class Clip(Processing):
    """Set tensor values below min to min and above max to max."""

    name: Literal["clip"] = "clip"

    kwargs: ClipKwargs


class ScaleLinearKwargs(ProcessingKwargs):
    axes: Optional[AxesInCZYX] = Field(None, examples=["xy"])
    """The subset of axes to scale jointly.
    For example xy to scale the two image axes for 2d data jointly."""

    gain: Union[float, Tuple[float, ...]] = 1.0
    """multiplicative factor"""

    offset: Union[float, Tuple[float, ...]] = 0.0
    """additive term"""

    @model_validator(mode="after")
    def either_gain_or_offset(self):
        if (self.gain == 1.0 or isinstance(self.gain, tuple) and all(g == 1.0 for g in self.gain)) and (
            self.offset == 0.0 or isinstance(self.offset, tuple) and all(off == 0.0 for off in self.offset)
        ):
            raise ValueError("Redunt linear scaling not allowd. Set `gain` != 1.0 and/or `offset` != 0.0.")

        return self


class ScaleLinear(Processing):
    """Fixed linear scaling."""

    name: Literal["scale_linear"] = "scale_linear"
    kwargs: ScaleLinearKwargs


class Sigmoid(Processing):
    """The logistic sigmoid funciton, a.k.a. expit function."""

    name: Literal["sigmoid"] = "sigmoid"


class ZeroMeanUnitVarianceKwargs(ProcessingKwargs):
    mode: Literal["fixed", "per_dataset", "per_sample"] = Field("fixed", description=_MODE_DESCR)
    axes: AxesInCZYX = Field(examples=["xy"])
    """The subset of axes to normalize jointly.
    For example `xy` to normalize the two image axes for 2d data jointly."""

    mean: Union[float, NonEmpty[Tuple[float, ...]], None] = Field(None, examples=[(1.1, 2.2, 3.3)])
    """The mean value(s) to use for `mode: fixed`.
    For example `[1.1, 2.2, 3.3]` in the case of a 3 channel image with `axes: xy`."""
    # todo: check if means match input axes (for mode 'fixed')

    std: Union[float, NonEmpty[Tuple[float, ...]], None] = Field(None, examples=[(0.1, 0.2, 0.3)])
    """The standard deviation values to use for `mode: fixed`. Analogous to mean."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`."""

    @model_validator(mode="after")
    def mean_and_std_match_mode(self):
        if self.mode == "fixed" and (self.mean is None or self.std is None):
            raise ValueError("`mean` and `std` are required for `mode: fixed`.")
        elif self.mode != "fixed" and (self.mean is not None or self.std is not None):
            raise ValueError(f"`mean` and `std` not allowed for `mode: {self.mode}`")

        return self


class ZeroMeanUnitVariance(Processing):
    """Subtract mean and divide by variance."""

    name: Literal["zero_mean_unit_variance"] = "zero_mean_unit_variance"
    kwargs: ZeroMeanUnitVarianceKwargs


class ScaleRangeKwargs(ProcessingKwargs):
    mode: Literal["per_dataset", "per_sample"]
    axes: AxesInCZYX = Field(examples=["xy"])
    """The subset of axes to normalize jointly.
    For example xy to normalize the two image axes for 2d data jointly."""

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


class ScaleRange(Processing):
    """Scale with percentiles."""

    name: Literal["scale_range"] = "scale_range"
    kwargs: ScaleRangeKwargs


class ScaleMeanVarianceKwargs(ProcessingKwargs):
    mode: Literal["per_dataset", "per_sample"]
    reference_tensor: Identifier
    """Name of tensor to match."""

    axes: Optional[AxesInCZYX] = Field(None, examples=["xy"])
    """The subset of axes to scale jointly.
    For example xy to normalize the two image axes for 2d data jointly.
    Default: scale all non-batch axes jointly."""

    eps: Annotated[float, Interval(gt=0, le=0.1)] = 1e-6
    """Epsilon for numeric stability:
    "`out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean."""


class ScaleMeanVariance(Processing):
    """Scale the tensor s.t. its mean and variance match a reference tensor."""

    name: Literal["scale_mean_variance"] = "scale_mean_variance"
    kwargs: ScaleMeanVarianceKwargs


Preprocessing = Annotated[
    Union[Binarize, Clip, ScaleLinear, Sigmoid, ZeroMeanUnitVariance, ScaleRange], Field(discriminator="name")
]
Postprocessing = Annotated[
    Union[Binarize, Clip, ScaleLinear, Sigmoid, ZeroMeanUnitVariance, ScaleRange, ScaleMeanVariance],
    Field(discriminator="name"),
]


class InputTensor(TensorBase):
    data_type: Literal["float32", "uint8", "uint16"]
    """For now an input tensor is expected to be given as `float32`.
    The data flow in bioimage.io models is explained
    [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit)."""

    shape: Union[Tuple[int, ...], ParametrizedInputShape] = Field(
        examples=[(1, 512, 512, 1), dict(min=(1, 64, 64, 1), step=(0, 32, 32, 0))]
    )
    """Specification of input tensor shape."""

    preprocessing: Tuple[Preprocessing, ...] = ()
    """Description of how this input should be preprocessed."""

    @model_validator(mode="after")
    def zero_batch_step_and_one_batch_size(self):
        bidx = self.axes.find("b")
        if bidx == -1:
            return self

        if isinstance(self.shape, ParametrizedInputShape):
            step = self.shape.step
            shape = self.shape.min
            if step[bidx] != 0:
                raise ValueError(
                    "Input shape step has to be zero in the batch dimension (the batch dimension can always be "
                    "increased, but `step` should specify how to increase the minimal shape to find the largest "
                    "single batch shape)"
                )
        else:
            shape = self.shape

        if shape[bidx] != 1:
            raise ValueError("Input shape has to be 1 in the batch dimension b.")

        return self

    @model_validator(mode="after")
    def validate_preprocessing_kwargs(self):
        for p in self.preprocessing:
            kwarg_axes = p.kwargs.get("axes", "")
            if any(a not in self.axes for a in kwarg_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes")

        return self


class OutputTensor(TensorBase):
    data_type: Literal[
        "float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64", "bool"
    ]
    """Data type.
    The data flow in bioimage.io models is explained
    [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit)."""

    shape: Union[Tuple[int, ...], ImplicitOutputShape]
    """Output tensor shape."""

    halo: Optional[Tuple[int, ...]] = None
    """The `halo` that should be cropped from the output tensor to avoid boundary effects.
    The `halo` is to be cropped from both sides, i.e. `shape_after_crop = shape - 2 * halo`.
    To document a `halo` that is already cropped by the model `shape.offset` has to be used instead."""

    postprocessing: Tuple[Postprocessing, ...] = ()
    """Description of how this output should be postprocessed."""

    @model_validator(mode="after")
    def matching_halo_length(self):
        if self.halo and len(self.halo) != len(self.shape):
            raise ValueError(f"halo {self.halo} has to have same length as shape {self.shape}!")

        return self

    @model_validator(mode="after")
    def validate_postprocessing_kwargs(self):
        for p in self.postprocessing:
            kwarg_axes = p.kwargs.get("axes", "")
            if any(a not in self.axes for a in kwarg_axes):
                raise ValueError("`kwargs.axes` needs to be subset of axes")

        return self


KnownRunMode = Literal["deepimagej"]


class RunMode(Node):
    name: Annotated[Union[KnownRunMode, str], warn(KnownRunMode)]
    """Run mode name"""

    kwargs: Kwargs = Field(default_factory=dict)
    """Run mode specific key word arguments"""


class ModelRdf(Node):
    rdf_source: FileSource = Field(alias="uri")
    """URL or relative path of a model RDF"""

    sha256: Sha256
    """SHA256 checksum of the model RDF specified under `rdf_source`."""


class LinkedModel(LinkedResource):
    """Reference to a bioimage.io model."""

    id: NonEmpty[str]
    """A valid model `id` from the bioimage.io collection."""


class Model(GenericBaseNoSource):
    """Specification of the fields used in a bioimage.io-compliant RDF that describes AI models with pretrained weights.

    These fields are typically stored in a YAML file which we call a model resource description file (model RDF).
    Like any RDF, a model RDF can be downloaded from or uploaded to the bioimage.io website and is produced or consumed
    by bioimage.io-compatible consumers (e.g. image analysis software or another website).
    """

    model_config = ConfigDict(
        {
            **GenericBaseNoSource.model_config,
            **ConfigDict(title="bioimage.io model specification"),
        }
    )
    """pydantic model_config"""

    format_version: Literal["0.4.9",] = "0.4.9"
    """Version of the bioimage.io model description specification used.
    When creating a new model always use the latest micro/patch version described here.
    The `format_version` is important for any consumer software to understand how to parse the fields.
    """

    type: Literal["model"] = "model"
    """specialized type 'model'"""

    authors: NonEmpty[Tuple[Author, ...]]
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

    inputs: NonEmpty[Tuple[InputTensor, ...]]
    """Describes the input tensors expected by this model."""

    license: Annotated[Union[LicenseId, str], warn(LicenseId)] = Field(examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"])
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do notsupport custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
    to discuss your intentions with the community."""

    name: Annotated[
        CapitalStr,
        warn(MaxLen(64), INFO),
    ]
    """"A human-readable name of this model.
    It should be no longer than 64 characters and only contain letter, number, underscore, minus or space characters."""

    outputs: NonEmpty[Tuple[OutputTensor, ...]]
    """Describes the output tensors."""

    @field_validator("inputs", "outputs")
    @classmethod
    def unique_tensor_names(cls, value: Sequence[Union[InputTensor, OutputTensor]]):
        unique_names = {v.name for v in value}
        if len(unique_names) != len(value):
            raise ValueError("Duplicate tensor names")
        return value

    @model_validator(mode="after")
    def unique_io_names(self):
        unique_names = {ss.name for s in (self.inputs, self.outputs) for ss in s}
        if len(unique_names) != (len(self.inputs) + len(self.outputs)):
            raise ValueError("Duplicate tensor names across inputs/outputs")

        return self

    @model_validator(mode="after")
    def minimum_shape2valid_output(self):
        tensors_by_name: Dict[str, Union[InputTensor, OutputTensor]] = {t.name: t for t in self.inputs + self.outputs}

        for out in self.outputs:
            if isinstance(out.shape, ImplicitOutputShape):
                ndim_ref = len(tensors_by_name[out.shape.reference_tensor].shape)
                ndim_out_ref = len([scale for scale in out.shape.scale if scale is not None])
                if ndim_ref != ndim_out_ref:
                    expanded_dim_note = (
                        f" Note that expanded dimensions (`scale`: null) are not counted for {out.name}'s"
                        "dimensionality here."
                        if None in out.shape.scale
                        else ""
                    )
                    raise ValueError(
                        f"Referenced tensor '{out.shape.reference_tensor}' "
                        f"with {ndim_ref} dimensions does not match "
                        f"output tensor '{out.name}' with {ndim_out_ref} dimensions.{expanded_dim_note}"
                    )

            min_out_shape = self._get_min_shape(out, tensors_by_name)
            if out.halo:
                halo = out.halo
                halo_msg = f" for halo {out.halo}"
            else:
                halo = [0] * len(min_out_shape)
                halo_msg = ""

            if any([s - 2 * h < 1 for s, h in zip(min_out_shape, halo)]):
                raise ValueError(f"Minimal shape {min_out_shape} of output {out.name} is too small{halo_msg}.")

        return self

    @classmethod
    def _get_min_shape(
        cls, t: Union[InputTensor, OutputTensor], tensors_by_name: Dict[str, Union[InputTensor, OutputTensor]]
    ) -> Tuple[int, ...]:
        """output with subtracted halo has to result in meaningful output even for the minimal input
        see https://github.com/bioimage-io/spec-bioimage-io/issues/392
        """
        if isinstance(t.shape, tuple):
            return t.shape

        if isinstance(t.shape, ParametrizedInputShape):
            return t.shape.min

        assert isinstance(t.shape, ImplicitOutputShape)
        ref_shape = cls._get_min_shape(tensors_by_name[t.shape.reference_tensor], tensors_by_name)

        if None not in t.shape.scale:
            scale: Sequence[float, ...] = t.shape.scale  # type: ignore
        else:
            expanded_dims = tuple(idx for idx, sc in enumerate(t.shape.scale) if sc is None)
            new_ref_shape: List[int] = []
            for idx in range(len(t.shape.scale)):
                ref_idx = idx - sum(int(exp < idx) for exp in expanded_dims)
                new_ref_shape.append(1 if idx in expanded_dims else ref_shape[ref_idx])
            ref_shape = tuple(new_ref_shape)
            assert len(ref_shape) == len(t.shape.scale)
            scale = [0.0 if sc is None else sc for sc in t.shape.scale]

        offset = t.shape.offset
        assert len(offset) == len(scale)
        return tuple(int(rs * s + 2 * off) for rs, s, off in zip(ref_shape, scale, offset))

    @model_validator(mode="after")
    def validate_tensor_references_in_inputs(self):
        for t in self.inputs:
            for proc in t.preprocessing:
                if "reference_tensor" not in proc.kwargs:
                    continue

                ref_tensor = proc.kwargs["reference_tensor"]
                if ref_tensor not in {t.name for t in self.inputs}:
                    raise ValueError(f"'{ref_tensor}' not found in inputs")

                if ref_tensor == t.name:
                    raise ValueError(f"invalid self reference for preprocessing of tensor {t.name}")

        return self

    @model_validator(mode="after")
    def validate_tensor_references_in_outputs(self):
        for t in self.outputs:
            for proc in t.postprocessing:
                if "reference_tensor" not in proc.kwargs:
                    continue
                ref_tensor = proc.kwargs["reference_tensor"]
                if ref_tensor not in {t.name for t in self.inputs}:
                    raise ValueError(f"{ref_tensor} not found in inputs")

        return self

    packaged_by: Tuple[Author, ...] = ()
    """The persons that have packaged and uploaded this model.
    Only required if those persons differ from the `authors`."""

    parent: Optional[Union[LinkedModel, ModelRdf]] = None
    """The model from which this model is derived, e.g. by fine-tuning the weights."""

    run_mode: Optional[RunMode] = None
    """Custom run mode for this model: for more complex prediction procedures like test time
    data augmentation that currently cannot be expressed in the specification.
    No standard run modes are defined yet."""

    sample_inputs: Tuple[FileSource, ...] = Field((), in_package=True)
    """URLs/relative paths to sample inputs to illustrate possible inputs for the model,
    for example stored as PNG or TIFF images.
    The sample files primarily serve to inform a human user about an example use case"""

    sample_outputs: Tuple[FileSource, ...] = Field((), in_package=True)
    """URLs/relative paths to sample outputs corresponding to the `sample_inputs`."""

    test_inputs: NonEmpty[Tuple[Annotated[FileSource, WithSuffix(".npy", case_sensitive=True)], ...]] = Field(
        in_package=True
    )
    """URLs or relative paths to test input tensors compatible with the `inputs` description for **a single test case**.
    This means if your model has more than one input, you should provide one URL/relative path for each input.
    Each test input should be a file with an ndarray in
    [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
    The extension must be '.npy'."""

    test_outputs: NonEmpty[Tuple[Annotated[FileSource, WithSuffix(".npy", case_sensitive=True)], ...]] = Field(
        in_package=True
    )
    """Analog to `test_inputs`."""

    timestamp: Datetime
    """Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
    with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)."""

    training_data: Union[LinkedDataset, Dataset, None] = None
    """The dataset used to train this model"""

    weights: Weights
    """The weights for this model.
    Weights can be given for different formats, but should otherwise be equivalent.
    The available weight formats determine which consumers can use this model."""

    @staticmethod
    def convert_model_from_v0_4_0_to_0_4_1(data: Dict[str, Any]):
        # move dependencies from root to pytorch_state_dict weights entry
        deps = data.pop("dependencies", None)
        weights = data.get("weights", {})
        if deps and weights and isinstance(weights, dict):
            entry = weights.get("pytorch_state_dict")
            if entry and isinstance(entry, dict):
                entry["dependencies"] = deps

        data["format_version"] = "0.4.1"

    @staticmethod
    def convert_model_from_v0_4_4_to_0_4_5(data: Dict[str, Any]) -> None:
        parent = data.pop("parent", None)
        if parent and "uri" in parent:
            data["parent"] = parent["uri"]

        data["format_version"] = "0.4.5"

    @classmethod
    def convert_from_older_format(cls, data: RawDict) -> None:
        fv = data.get("format_version", "0.3.0")
        if isinstance(fv, str):
            major_minor = tuple(map(int, fv.split(".")[:2]))
            if major_minor < (0, 4):
                convert_model_from_v0_3_to_0_4_0(data)
            elif major_minor > (0, 4):
                return

        if data["format_version"] == "0.4.0":
            cls.convert_model_from_v0_4_0_to_0_4_1(data)

        if data["format_version"] in ("0.4.1", "0.4.2", "0.4.3", "0.4.4"):
            cls.convert_model_from_v0_4_4_to_0_4_5(data)

        if data["format_version"] in ("0.4.5", "0.4.6"):
            cls._remove_slashes_from_names(data)
            data["format_version"] = "0.4.7"

        if data["format_version"] in ("0.4.7", "0.4.8"):
            data["format_version"] = "0.4.9"

        # remove 'future' from config if no other than the used future entries exist
        config = data.get("config", {})
        if isinstance(config, dict) and config.get("future") == {}:
            del config["future"]

        # remove 'config' if now empty
        if data.get("config") == {}:
            del data["config"]


AnyModel = Model
