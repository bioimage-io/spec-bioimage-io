import collections.abc
from typing import Annotated, Any, ClassVar, Dict, List, Literal, Mapping, Optional, Set, Tuple, Union

from annotated_types import Ge, Gt, MaxLen
from pydantic import ConfigDict, FieldValidationInfo, field_validator, model_validator

from bioimageio.spec import generic
from bioimageio.spec._internal._constants import SHA256_HINT
from bioimageio.spec._internal._utils import Field
from bioimageio.spec._internal._warn import warn
from bioimageio.spec.dataset import Dataset
from bioimageio.spec.dataset.v0_3 import LinkedDataset
from bioimageio.spec.shared.nodes import FrozenDictNode, Node
from bioimageio.spec.shared.types import (
    CapitalStr,
    Datetime,
    FileSource,
    Identifier,
    LicenseId,
    NonEmpty,
    RawDict,
    RawLeafValue,
    Sha256,
    SiUnit,
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
OtherTensorAxisId = Annotated[str, MaxLen(33)]
TensorAxisId = Union[ShortId, OtherTensorAxisId]
SAME_AS_TYPE = "<same as type>"


class ParametrizedSize(Node):
    """Describes a range of valid tensor axis sizes"""

    min: Annotated[int, Gt(0)]
    step: Annotated[int, Gt(0)]
    step_with: Union[TensorAxisId, Literal["BATCH_AXES"], None] = None
    """name of another axis to resize jointly,
    i.e. `n=n_other` for `size = min + n*step`, `size_other = min_other + n_other*step_other`.
    To step with an axis of another tensor, use `step_with = <tensor name>.<axis name>`.
    `step_with="BATCH_AXES"` is a special value to step jointly with all batch dimensions.
    """


class ParametrizedBatchSize(ParametrizedSize):
    """Any batch axis size must be parametrized by `min=1`, `step=1` and `step_with` all batch axes jointly."""

    min: Literal[1] = 1
    step: Literal[1] = 1
    step_with: Literal["BATCH_AXES"] = "BATCH_AXES"


class SizeReference(Node):
    """A tensor axis size defined in relation to another `reference` tensor axis

    `size = reference.size / reference.scale * axis.scale + offset`
    The axis and the referenced axis need to have the same unit (or no unit).
    `scale=1.0`, if the axes have a no scale.
    """

    reference: TensorAxisId
    offset: Annotated[int, Ge(0)] = 0


# this Axis definition is compatible with the NGFF draft from July 10, 2023
# https://ngff.openmicroscopy.org/latest/#axes-md
class AxisBase(Node):
    type: Literal["batch", "channel", "index", "time", "space"]

    name: ShortId
    """a unique name"""

    description: Annotated[str, MaxLen(128)] = ""

    size: Union[Annotated[int, Gt(0)], ParametrizedSize, SizeReference, TensorAxisId]
    """The axis size.
    To specify that this axis' size equals another, an axis name can be given.
    Specify another tensor's axis as `<tensor name>.<axis name>`."""


class WithHalo(Node):
    halo: Annotated[int, Ge(0)] = 0
    """The halo should be cropped from the output tensor to avoid boundary effects.
    It is to be cropped from both sides, i.e. `size_after_crop = size - 2 * halo`.
    To document a halo that is already cropped by the model use `size.offset` instead."""


class BatchAxis(AxisBase):
    type: Literal["batch"] = "batch"
    name: ShortId = "batch"
    size: ParametrizedBatchSize = ParametrizedBatchSize()


class ChannelAxis(AxisBase):
    type: Literal["channel"] = "channel"
    name: ShortId = "channel"
    channel_names: Tuple[ShortId, ...]
    size: Union[Annotated[int, Gt(0)], Literal["#channel_names"]] = "#channel_names"

    def model_post_init(self, __context: Any):
        if self.size == "#channel_names":
            object.__setattr__(self, "size", len(self.channel_names))
        return super().model_post_init(__context)


class IndexAxis(AxisBase):
    type: Literal["index"] = "index"
    name: ShortId = "index"


class TimeAxis(AxisBase):
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


class SpaceAxis(AxisBase):
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


class TensorValueBase(Node):
    description: Annotated[str, MaxLen(128)] = ""
    """Brief descripiton of tensor values"""


class NominalTensorValue(TensorValueBase):
    type: Literal["nominal"] = "nominal"
    values: Tuple[Union[int, float, str, bool], ...]


class OrdinalTensorValue(TensorValueBase):
    type: Literal["ordinal"] = "ordinal"
    values: Tuple[Union[int, float, str, bool], ...]
    """values in ascending order"""


class IntervalTensorValueBase(TensorValueBase):
    unit: Optional[SiUnit] = None
    factor: float = 1.0
    data_type: Literal["float32", "float64", "uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64"]
    data_range: Tuple[Optional[float], Optional[float]] = (
        None,
        None,
    )
    """Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
    `None` correspond to min/max of what can be expressed by `data_type`."""


class IntervalTensorValue(IntervalTensorValueBase):
    type: Literal["interval"] = "interval"


class RatioTensorValue(IntervalTensorValueBase):
    type: Literal["ratio"] = "ratio"
    offset: float = 0.0


TensorValue = Annotated[
    Union[NominalTensorValue, OrdinalTensorValue, IntervalTensorValue, RatioTensorValue], Field(discriminator="type")
]


class TensorBase(Node):
    name: Identifier  # todo: validate duplicates
    """Tensor name. No duplicates are allowed."""

    description: Annotated[str, MaxLen(128)] = ""
    """Brief descripiton of the tensor"""

    axes: Tuple[Axis, ...]

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

    values: Union[TensorValue, Tuple[TensorValue, ...]]
    """Description of tensor values, optionally per channel.
    If specified per channel, `data_type` needs to match across channels for interval and ratio type values."""

    @field_validator("axes", mode="after")
    @classmethod
    def validate_axes(cls, axes: Tuple[Axis, ...]):
        seen: Set[str] = set()
        duplicate_axes_names: Set[str] = set()
        for a in axes:
            (duplicate_axes_names if a.name in seen else seen).add(a.name)

        if duplicate_axes_names:
            raise ValueError(f"Duplicate axis names: {duplicate_axes_names}")

        return axes


class InputTensor(TensorBase):
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
    axes: Tuple[OutputAxis, ...]

    postprocessing: Tuple[v0_4.Postprocessing, ...] = ()
    """Description of how this output should be postprocessed."""

    @model_validator(mode="after")
    def validate_postprocessing_kwargs(self):
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

    kwargs: FrozenDictNode[NonEmpty[str], RawLeafValue] = Field(default_factory=dict)
    """key word arguments for the `callable`"""


class ArchitectureFromDependency(Node):
    callable: v0_4.CallableFromDepencency = Field(examples=["my_module.submodule.get_my_model"])
    """callable returning a torch.nn.Module instance.
    `<dependency-package>.<[dependency-module]>.<identifier>`."""

    kwargs: FrozenDictNode[NonEmpty[str], RawLeafValue] = Field(default_factory=dict)
    """key word arguments for the `callable`"""


Architecture = Union[ArchitectureFromSource, ArchitectureFromDependency]


class PytorchStateDictEntry(v0_4.WeightsEntryBase):
    type: Literal["pytorch_state_dict"] = Field("pytorch_state_dict", exclude=True)
    weights_format_name: ClassVar[str] = "Pytorch State Dict"
    architecture: Architecture

    pytorch_version: Annotated[Union[Version, None], warn(Version)] = None
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


class ModelRdf(Node):
    rdf_source: FileSource
    """URL or relative path to a model RDF"""

    sha256: Sha256
    """SHA256 checksum of the model RDF specified under `rdf_source`."""


class Model(
    generic.v0_3.GenericBaseNoSource
):  # todo: do not inherite from v0_4.Model, e.g. 'inputs' are not compatible
    """Specification of the fields used in a bioimage.io-compliant RDF to describe AI models with pretrained weights.

    These fields are typically stored in a YAML file which we call a model resource description file (model RDF).
    Like any RDF, a model RDF can be downloaded from or uploaded to the bioimage.io website and is produced or consumed
    by bioimage.io-compatible consumers (e.g. image analysis software or another website).
    """

    model_config = ConfigDict(
        {
            **generic.v0_3.GenericBaseNoSource.model_config,
            **ConfigDict(title="bioimage.io model specification"),
        }
    )
    """pydantic model_config"""

    format_version: Literal["0.5.0"] = "0.5.0"

    type: Literal["model"] = "model"
    """specialized type 'model'"""

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

    inputs: NonEmpty[Tuple[InputTensor, ...]]
    """Describes the input tensors expected by this model."""

    @field_validator("inputs", mode="after")
    @classmethod
    def validate_input_axes(cls, inputs: Tuple[InputTensor]) -> Tuple[InputTensor]:
        tensor_axes_names = [f"{ipt.name}.{a.name}" for ipt in inputs for a in ipt.axes if not isinstance(a.size, str)]
        for i, ipt in enumerate(inputs):
            valid_axes_references = (
                ["BATCH_AXES", None] + [a.name for a in ipt.axes if not isinstance(a.size, str)] + tensor_axes_names
            )
            for a, ax in enumerate(ipt.axes):
                if isinstance(ax.size, ParametrizedSize) and ax.size.step_with not in valid_axes_references:
                    raise ValueError(
                        f"Invalid tensor axis reference at inputs[{i}].axes[{a}].size.step_with: {ax.size.step_with}."
                    )
                if isinstance(ax.size, str) and ax.size not in valid_axes_references:
                    raise ValueError(f"Invalid tensor axis reference at inputs[{i}].axes[{a}].size: {ax.size}.")

        return inputs

    license: LicenseId = Field(examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"])
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do notsupport custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
    to discuss your intentions with the community."""

    name: Annotated[
        CapitalStr,
        warn(MaxLen(64)),
    ] = Field(pattern=r"\w+[\w\- ]*\w")
    """"A human-readable name of this model.
    It should be no longer than 64 characters
    and may only contain letter, number, underscore, minus or space characters."""

    outputs: NonEmpty[Tuple[OutputTensor, ...]]
    """Describes the output tensors."""

    @field_validator("outputs", mode="after")
    @classmethod
    def validate_output_axes(cls, outputs: Tuple[OutputTensor], info: FieldValidationInfo) -> Tuple[OutputTensor]:
        input_tensor_axes_names = [
            f"{ipt.name}.{a.name}"
            for ipt in info.data.get("inputs", ())
            for a in ipt.axes
            if not isinstance(a.size, str)
        ]
        output_tensor_axes_names = [
            f"{out.name}.{a.name}" for out in outputs for a in out.axes if not isinstance(a.size, str)
        ]

        for i, out in enumerate(outputs):
            valid_axes_references = (
                [None]
                + [a.name for a in out.axes if not isinstance(a.size, str)]
                + input_tensor_axes_names
                + output_tensor_axes_names
            )
            for a, ax in enumerate(out.axes):
                if isinstance(ax.size, ParametrizedSize) and ax.size.step_with not in valid_axes_references:
                    raise ValueError(
                        f"Invalid tensor axis reference outputs[{i}].axes[{a}].size.step_with: {ax.size.step_with}."
                    )
                if isinstance(ax.size, str) and ax.size not in valid_axes_references:
                    raise ValueError(f"Invalid tensor axis reference at outputs[{i}].axes[{a}].size: {ax.size}.")

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
    def convert_from_older_format(cls, data: RawDict) -> None:
        fv = data.get("format_version")
        if not isinstance(fv, str) or fv.count(".") != 3:
            return

        major, minor, _ = map(int, fv.split("."))
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
            if isinstance(test_tensors, collections.Sequence) and len(test_tensors) == len(tensor_specs):
                param["test_tensor"] = test_tensors[i]

            if isinstance(sample_tensors, collections.Sequence) and len(sample_tensors) == len(tensor_specs):
                param["sample_tensor"] = sample_tensors[i]

    @classmethod
    def convert_model_from_v0_4_to_0_5_0(cls, data: RawDict) -> None:
        cls._convert_axes_string_to_axis_descriptions(data)
        cls._convert_architecture_field(data)
        data.pop("download_url", None)

        data["format_version"] = "0.5.0"

    @classmethod
    def _convert_axes_string_to_axis_descriptions(cls, data: RawDict):
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

    @staticmethod
    def _convert_architecture_field(data: Dict[str, Any]) -> None:
        weights: "Any | Dict[str, Any]" = data.get("weights")
        if not isinstance(weights, dict):
            return

        state_dict_entry: "Any | Dict[str, Any]" = weights.get("pytorch_state_dict")  # type: ignore
        if not isinstance(state_dict_entry, dict):
            return

        callable_ = state_dict_entry.pop("architecture")  # type: ignore
        sha = state_dict_entry.pop("architecture_sha256")  # type: ignore
        state_dict_entry["architecture"] = dict(callable=callable_, sha256=sha)  # type: ignore
        kwargs = state_dict_entry.pop("kwargs")  # type: ignore
        if kwargs:
            state_dict_entry["architecture"]["kwargs"] = kwargs  # type: ignore


AnyModel = Annotated[Union[v0_4.Model, Model], Field(discriminator="format_version")]
