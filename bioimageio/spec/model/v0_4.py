from __future__ import annotations

import collections.abc
from datetime import datetime
from string import ascii_letters, digits
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    get_args,
)

from annotated_types import Ge, Len, MinLen, MultipleOf, Predicate
from pydantic import (
    AllowInfNan,
    HttpUrl,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated

from bioimageio.spec.dataset.v0_2 import Dataset, LinkedDataset
from bioimageio.spec.generic.v0_2 import (
    Attachments,
    Author,
    LinkedResource,
    ResourceDescriptionBaseNoSource,
)
from bioimageio.spec.shared.common import SHA256_HINT
from bioimageio.spec.shared.fields import Field
from bioimageio.spec.shared.nodes import FrozenDictNode, Kwargs, Node, StringNode
from bioimageio.spec.shared.types import (
    CapitalStr,
    FileSource,
    Identifier,
    LicenseId,
    NonEmpty,
    RawMapping,
    RelativeFilePath,
    Sha256,
    Version,
)
from bioimageio.spec.shared.validation import (
    AfterWarner,
    validate_datetime_iso8601,
    validate_suffix,
    warn,
)

LatestFormatVersion = Literal["0.4.9"]
FormatVersion = Literal[
    "0.4.0", "0.4.1", "0.4.2", "0.4.3", "0.4.4", "0.4.5", "0.4.6", "0.4.7", "0.4.8", LatestFormatVersion
]
Framework = Literal["pytorch", "tensorflow"]
Language = Literal["python", "java"]
PostprocessingName = Literal[
    "binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range", "scale_mean_variance"
]
PreprocessingName = Literal["binarize", "clip", "scale_linear", "sigmoid", "zero_mean_unit_variance", "scale_range"]


LATEST_FORMAT_VERSION: LatestFormatVersion = get_args(LatestFormatVersion)[0]


class CallableFromDepencency(StringNode):
    module_name: str
    callable_name: str

    must_include = (".",)

    @model_validator(mode="before")
    @classmethod
    def load(cls, data: Any) -> Dict[str, str]:
        str_data = cls.sanitize(data)
        *mods, callname = str_data.split(".")
        modnane = ".".join(mods)
        return dict(module_name=modnane, callable_name=callname)


class CallableFromSourceFile(StringNode):
    source_file: Union[HttpUrl, RelativeFilePath] = Field(in_package=True)
    callable_name: str

    def __str__(self):
        return f"{self.source_file}{self.split_on}{self.callable_name}"

    @model_validator(mode="before")
    @classmethod
    def load(cls, data: Any) -> Dict[str, str]:
        str_data = cls.sanitize(data)
        *file_parts, callname = str_data.split(cls.split_on)
        return dict(source_file=cls.split_on.join(file_parts), callable_name=callname)


CustomCallable = Union[CallableFromSourceFile, CallableFromDepencency]


class Dependencies(StringNode):
    manager: NonEmpty[str] = Field(examples=["conda", "maven", "pip"])
    """Dependency manager"""

    file: Union[HttpUrl, RelativeFilePath] = Field(
        in_package=True, examples=["environment.yaml", "pom.xml", "requirements.txt"]
    )
    """Dependency file"""

    def __str__(self):
        return f"{self.manager}:{self.file}"

    @model_validator(mode="before")
    @classmethod
    def load(cls, data: Any) -> Dict[str, str]:
        data = cls.sanitize(data)
        manager, *file_parts = data.split(cls.split_on)
        return dict(manager=manager, file=cls.split_on.join(file_parts))


WeightsFormat = Literal[
    "pytorch_state_dict",
    "torchscript",
    "keras_hdf5",
    "tensorflow_js",
    "tensorflow_saved_model_bundle",
    "onnx",
]


class WeightsEntryBase(Node):
    model_config = {**Node.model_config, "exclude": ("type",)}
    weights_format_name: ClassVar[str]  # human readable
    type: WeightsFormat
    """weights format of this entry"""

    source: Union[HttpUrl, RelativeFilePath] = Field(in_package=True)
    """The weights file."""

    sha256: Union[Sha256, None] = Field(None, description="SHA256 checksum of the source file\n" + SHA256_HINT)
    """SHA256 checksum of the source file"""

    attachments: Union[Attachments, None] = None
    """Attachments that are specific to this weights entry."""

    authors: Union[Tuple[Author, ...], None] = None
    """Authors:
    If this is the initial weights entry (in other words: it does not have a `parent` field):
        the person(s) that have trained this model.
    If this is a child weight (it has a `parent` field):
        the person(s) who have converted the weights to this format.
    """

    dependencies: Union[Dependencies, None] = Field(
        None, examples=["conda:environment.yaml", "maven:./pom.xml", "pip:./requirements.txt"]
    )
    """"Dependency manager and dependency file, specified as `<dependency manager>:<relative file path>`."""

    parent: Union[WeightsFormat, None] = Field(None, examples=["pytorch_state_dict"])
    """The source weights these weights were converted from.
    For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
    The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
    All weight entries except one (the initial set of weights resulting from training the model),
    need to have this field."""
    # todo: validate


class KerasHdf5Entry(WeightsEntryBase):
    type: Literal["keras_hdf5"] = Field("keras_hdf5", exclude=True)
    weights_format_name: ClassVar[str] = "Keras HDF5"
    tensorflow_version: Union[Version, None] = None
    """TensorFlow version used to create these weights"""


class OnnxEntry(WeightsEntryBase):
    type: Literal["onnx"] = Field("onnx", exclude=True)
    weights_format_name: ClassVar[str] = "ONNX"
    opset_version: Union[Annotated[int, warn(Ge(7))], None] = None
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
    def check_architecture_sha256(self, data: Any):
        if isinstance(data["architecture"], CallableFromSourceFile):
            if data.get("architecture_sha256") is None:
                raise ValueError("Missing required `architecture_sha256` for `architecture` with source file.")
        elif data.get("architecture_sha256") is not None:
            raise ValueError("Got `architecture_sha256` for architecture that does not have a source file.")

        return data

    kwargs: Dict[NonEmpty[str], Any] = Field(default_factory=dict)
    """key word arguments for the `architecture` callable"""

    pytorch_version: Union[Version, None] = None
    """Version of the PyTorch library used.
    If `depencencies` is specified it should include pytorch and the verison should match.
    (`dependencies` overrules `pytorch_version`)"""


class TorchscriptEntry(WeightsEntryBase):
    type: Literal["torchscript"] = Field("torchscript", exclude=True)
    weights_format_name: ClassVar[str] = "TorchScript"


class TensorflowJsEntry(WeightsEntryBase):
    type: Literal["tensorflow_js"] = Field("tensorflow_js", exclude=True)
    weights_format_name: ClassVar[str] = "Tensorflow.js"
    tensorflow_version: Union[Version, None] = None
    """Version of the TensorFlow library used."""

    source: Union[HttpUrl, RelativeFilePath] = Field(in_package=True)
    """The multi-file weights.
    All required files/folders should be a zip archive."""


class TensorflowSavedModelBundleEntry(WeightsEntryBase):
    type: Literal["tensorflow_saved_model_bundle"] = Field("tensorflow_saved_model_bundle", exclude=True)
    weights_format_name: ClassVar[str] = "Tensorflow Saved Model"
    tensorflow_version: Union[Version, None] = None
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

    min: Annotated[Tuple[int, ...], MinLen(1)]
    """The minimum input shape"""

    step: Annotated[Tuple[int, ...], MinLen(1)]
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

    scale: Annotated[Tuple[Union[float, None], ...], MinLen(1)]
    """output_pix/input_pix for each dimension.
    'null' values indicate new dimensions, whose length is defined by 2*`offset`"""

    offset: Annotated[Tuple[Annotated[float, MultipleOf(0.5)], ...], MinLen(1)]
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

    axes: Annotated[str, Predicate(lambda axs: all(a in "bitczyx" for a in axs))]
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

    # todo: validate axes in processing
    # @model_validator(mode="after")
    # def validate_processing_kwargs(self, data: Any):
    #     axes = data["axes"]
    #     processing_list = data.get(self.processing_name, [])
    #     for processing in processing_list:
    #         kwargs = processing.kwargs or {}
    #         kwarg_axes = kwargs.get("axes", "")
    #         if any(a not in axes for a in kwarg_axes):
    #             raise ValidationError("`kwargs.axes` needs to be subset of axes")

    #     return data


class Preprocessing(Node):
    name: PreprocessingName
    """Preprocessing name"""

    kwargs: Kwargs = Field(
        default_factory=dict,
        description=(
            f"Key word arguments as described in [preprocessing spec]"
            f"(https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/preprocessing_spec_"
            f"{'_'.join(LATEST_FORMAT_VERSION.split('.')[:2])}.md)."
        ),
    )
    """Key word arguments"""


class Postprocessing(Node):
    name: PostprocessingName
    """Postprocessing name"""
    kwargs: Kwargs = Field(
        default_factory=dict,
        description=(
            f"Key word arguments as described in [postprocessing spec]"
            f"(https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/postprocessing_spec_"
            f"{'_'.join(LATEST_FORMAT_VERSION.split('.')[:2])}.md)."
        ),
    )
    """Key word arguments"""


class InputTensor(TensorBase):
    data_type: Literal["float32"]
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


class OutputTensor(TensorBase):
    data_type: Literal["float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64"]
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


KnownRunMode = Literal["deepimagej"]


class RunMode(Node):
    name: Annotated[Union[KnownRunMode, str], warn(KnownRunMode)]
    """Run mode name"""

    kwargs: Kwargs = Field(default_factory=dict)
    """Run mode specific key word arguments"""

    # @validates("name")
    # def warn_on_unrecognized_run_mode(self, value: str):
    #     if isinstance(value, str):
    #         self.warn("name", f"Unrecognized run mode '{value}'")


class ModelRdf(Node):
    rdf_source: Union[FileSource, None] = Field(None, alias="uri")
    """URL or relative path of a model RDF"""

    sha256: Sha256
    """SHA256 checksum of the model RDF specified under `rdf_source`."""


class LinkedModel(LinkedResource):
    """Reference to a bioimage.io model."""

    id: NonEmpty[str]
    """A valid model `id` from the bioimage.io collection."""


class Model(ResourceDescriptionBaseNoSource):
    """Specification of the fields used in a bioimage.io-compliant RDF that describes AI models with pretrained weights.

    These fields are typically stored in a YAML file which we call a model resource description file (model RDF).
    Like any RDF, a model RDF can be downloaded from or uploaded to the bioimage.io website and is produced or consumed
    by bioimage.io-compatible consumers (e.g. image analysis software or another website).
    """

    model_config = {
        **ResourceDescriptionBaseNoSource.model_config,
        **dict(title=f"bioimage.io model RDF spec {LATEST_FORMAT_VERSION}"),
    }
    """pydantic model_config"""

    format_version: LatestFormatVersion = LATEST_FORMAT_VERSION
    """Version of the bioimage.io model Resource Description File (RDF) specification used.
    This is important for any consumer software to understand how to parse the fields.
    The recommended behavior for the implementation is to keep backward compatibility and throw an error if the RDF
    content has an unsupported format version.
    """

    type: Literal["model"] = "model"

    authors: Annotated[Tuple[Author, ...], MinLen(1)]
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

    inputs: Annotated[Tuple[InputTensor, ...], MinLen(1)]
    """Describes the input tensors expected by this model."""

    license: LicenseId = Field(examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"])
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do notsupport custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
    to discuss your intentions with the community."""

    name: Annotated[
        CapitalStr, AfterWarner(lambda n: all(s in ascii_letters + digits + "_- " for s in n)), warn(Len(max_length=64))
    ]
    """"A human-readable name of this model.
    It should be no longer than 64 characters and only contain letter, number, underscore, minus or space characters."""

    outputs: Annotated[Tuple[OutputTensor, ...], MinLen(1)]
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

        # output with subtracted halo has to result in meaningful output even for the minimal input
        # see https://github.com/bioimage-io/spec-bioimage-io/issues/392
        def get_min_shape(t: Union[InputTensor, OutputTensor]) -> Tuple[int, ...]:
            if isinstance(t.shape, tuple):
                return t.shape

            if isinstance(t.shape, ParametrizedInputShape):
                return t.shape.min

            assert isinstance(t.shape, ImplicitOutputShape)
            ref_shape = get_min_shape(tensors_by_name[t.shape.reference_tensor])

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
                        f"Referenced tensor {out.shape.reference_tensor} "
                        f"with {ndim_ref} dimensions does not match "
                        f"output tensor {out.name} with {ndim_out_ref} dimensions.{expanded_dim_note}"
                    )

            min_out_shape = get_min_shape(out)
            if out.halo:
                halo = out.halo
                halo_msg = f" for halo {out.halo}"
            else:
                halo = [0] * len(min_out_shape)
                halo_msg = ""

            if any([s - 2 * h < 1 for s, h in zip(min_out_shape, halo)]):
                raise ValueError(f"Minimal shape {min_out_shape} of output {out.name} is too small{halo_msg}.")

        return self

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

    test_inputs: NonEmpty[Tuple[FileSource, ...]] = Field(in_package=True)
    """URLs or relative paths to test input tensors compatible with the `inputs` description for **a single test case**.
    This means if your model has more than one input, you should provide one URL/relative path for each input.
    Each test input should be a file with an ndarray in
    [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
    The extension must be '.npy'."""

    test_outputs: NonEmpty[Tuple[FileSource, ...]] = Field(in_package=True)
    """Analog to `test_inputs`."""

    @field_validator("test_inputs", "test_outputs", mode="after")
    @classmethod
    def check_suffix(cls, value: NonEmpty[Tuple[FileSource, ...]]):
        return tuple(validate_suffix(v, ".npy") for v in value)

    timestamp: datetime
    """Timestamp of the initial creation of this model in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format."""

    @field_validator("timestamp", mode="plain")
    @classmethod
    def check_datetime(cls, value: Any) -> datetime:
        """only accept iso 8601 string and datetime, but no other valid datetime input like int or float"""
        return validate_datetime_iso8601(value)

    training_data: Union[LinkedDataset, Dataset, None] = None
    """The dataset used to train this model"""

    weights: FrozenDictNode[WeightsFormat, WeightsEntry]
    """The weights for this model.
    Weights can be given for different formats, but should otherwise be equivalent.
    The available weight formats determine which consumers can use this model."""

    @field_validator("weights", mode="before")
    @classmethod
    def weights_type_from_key(
        cls, data: Union[Any, Mapping[Union[Any, str], Union[Any, Mapping[str, Any]]]]
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
    def convert_from_older_format(cls, data: RawMapping) -> RawMapping:
        data = dict(data)
        fv = data.get("format_version", "0.3.0")
        if isinstance(fv, str):
            major_minor = tuple(map(int, fv.split(".")[:2]))
            if major_minor < (0, 4):
                raise NotImplementedError("model RDF conversion for format_version < 0.4 no longer supported.")
            elif major_minor > (0, 4):
                return data

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

        return data
