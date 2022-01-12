import typing
from copy import deepcopy

from marshmallow import RAISE, ValidationError, missing as missing_, pre_load, validates, validates_schema

from bioimageio.spec.model.v0_3.schema import (
    KerasHdf5WeightsEntry,
    ModelParent,
    OnnxWeightsEntry,
    Postprocessing,
    Preprocessing,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
    _WeightsEntryBase,
    _common_sha256_hint,
)
from bioimageio.spec.rdf import v0_2 as rdf
from bioimageio.spec.shared import LICENSES, field_validators, fields
from bioimageio.spec.shared.common import get_args, get_args_flat
from bioimageio.spec.shared.schema import ImplicitOutputShape, ParametrizedInputShape, SharedBioImageIOSchema
from . import raw_nodes


class _BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class _TensorBase(_BioImageIOSchema):
    name = fields.String(
        required=True,
        validate=field_validators.Predicate("isidentifier"),
        bioimageio_description="Tensor name. No duplicates are allowed.",
    )
    description = fields.String()
    axes = fields.Axes(
        required=True,
        bioimageio_description="""Axes identifying characters from: bitczyx. Same length and order as the axes in `shape`.

    | character | description |
    | --- | --- |
    |  b  |  batch (groups multiple samples) |
    |  i  |  instance/index/element |
    |  t  |  time |
    |  c  |  channel |
    |  z  |  spatial dimension z |
    |  y  |  spatial dimension y |
    |  x  |  spatial dimension x |""",
    )
    data_type = fields.String(
        required=True,
        bioimageio_description="The data type of this tensor. For inputs, only `float32` is allowed and the consumer "
        "software needs to ensure that the correct data type is passed here. For outputs can be any of `float32, "
        "float64, (u)int8, (u)int16, (u)int32, (u)int64`. The data flow in bioimage.io models is explained "
        "[in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).",
    )
    data_range = fields.Tuple(
        (fields.Float(allow_nan=True), fields.Float(allow_nan=True)),
        bioimageio_description="Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor. "
        "If not specified, the full data range that can be expressed in `data_type` is allowed.",
    )
    shape: fields.Union

    processing_name: str

    @validates_schema
    def validate_processing_kwargs(self, data, **kwargs):
        axes = data.get("axes", [])
        processing_list = data.get(self.processing_name, [])
        for processing in processing_list:
            kwargs = processing.kwargs or {}
            kwarg_axes = kwargs.get("axes", "")
            if any(a not in axes for a in kwarg_axes):
                raise ValidationError("`kwargs.axes` needs to be subset of axes")


class InputTensor(_TensorBase):
    shape = fields.Union(
        [
            fields.ExplicitShape(
                bioimageio_description="Exact shape with same length as `axes`, e.g. `shape: [1, 512, 512, 1]`"
            ),
            fields.Nested(
                ParametrizedInputShape(),
                bioimageio_description="A sequence of valid shapes given by `shape = min + k * step for k in {0, 1, ...}`.",
            ),
        ],
        required=True,
        bioimageio_description="Specification of input tensor shape.",
    )
    preprocessing = fields.List(
        fields.Nested(Preprocessing()), bioimageio_description="Description of how this input should be preprocessed."
    )
    processing_name = "preprocessing"

    @validates_schema
    def zero_batch_step_and_one_batch_size(self, data, **kwargs):
        axes = data.get("axes")
        shape = data.get("shape")

        if axes is None or shape is None:
            raise ValidationError("Failed to validate batch_step=0 and batch_size=1 due to other validation errors")

        axes = data["axes"]
        shape = data["shape"]

        bidx = axes.find("b")
        if bidx == -1:
            return

        if isinstance(shape, raw_nodes.ParametrizedInputShape):
            step = shape.step
            shape = shape.min

        elif isinstance(shape, list):
            step = [0] * len(shape)
        else:
            raise ValidationError(f"Unknown shape type {type(shape)}")

        if step[bidx] != 0:
            raise ValidationError(
                "Input shape step has to be zero in the batch dimension (the batch dimension can always be "
                "increased, but `step` should specify how to increase the minimal shape to find the largest "
                "single batch shape)"
            )

        if shape[bidx] != 1:
            raise ValidationError("Input shape has to be 1 in the batch dimension b.")


class OutputTensor(_TensorBase):
    shape = fields.Union(
        [
            fields.ExplicitShape(),
            fields.Nested(
                ImplicitOutputShape(),
                bioimageio_description="In reference to the shape of an input tensor, the shape of the output "
                "tensor is `shape = shape(input_tensor) * scale + 2 * offset`.",
            ),
        ],
        required=True,
        bioimageio_description="Specification of output tensor shape.",
    )
    halo = fields.List(
        fields.Integer(),
        bioimageio_description="The halo to crop from the output tensor (for example to crop away boundary effects or "
        "for tiling). The halo should be cropped from both sides, i.e. `shape_after_crop = shape - 2 * halo`. The "
        "`halo` is not cropped by the bioimage.io model, but is left to be cropped by the consumer software. Use "
        "`shape:offset` if the model output itself is cropped and input and output shapes not fixed.",
    )
    postprocessing = fields.List(
        fields.Nested(Postprocessing()),
        bioimageio_description="Description of how this output should be postprocessed.",
    )
    processing_name = "postprocessing"

    @validates_schema
    def matching_halo_length(self, data, **kwargs):
        shape = data.get("shape")
        halo = data.get("halo")
        if halo is None:
            return
        elif isinstance(shape, list) or isinstance(shape, raw_nodes.ImplicitOutputShape):
            if shape is None or len(halo) != len(shape):
                raise ValidationError(f"halo {halo} has to have same length as shape {shape}!")
        else:
            raise NotImplementedError(type(shape))


class PytorchStateDictWeightsEntry(_WeightsEntryBase):
    raw_nodes = raw_nodes

    bioimageio_description = "PyTorch state dictionary weights format"
    weights_format = fields.String(validate=field_validators.Equal("pytorch_state_dict"), required=True, load_only=True)
    architecture = fields.ImportableSource(
        required=True,
        bioimageio_description="Source code of the model architecture that either points to a "
        "local implementation: `<relative path to file>:<identifier of implementation within the file>` or the "
        "implementation in an available dependency: `<root-dependency>.<sub-dependency>.<identifier>`.\nFor example: "
        "`my_function.py:MyImplementation` or `bioimageio.core.some_module.some_class_or_function`.",
    )
    architecture_sha256 = fields.String(
        bioimageio_maybe_required=True,
        validate=field_validators.Length(equal=64),
        bioimageio_description="SHA256 checksum of the model source code file."
        + _common_sha256_hint
        + " This field is only required if the architecture points to a source file.",
    )
    dependencies = fields.Dependencies(
        bioimageio_description="Dependency manager and dependency file, specified as `<dependency manager>:<relative "
        "path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'"
    )

    kwargs = fields.Kwargs(
        bioimageio_description="Keyword arguments for the implementation specified by `architecture`."
    )

    @validates_schema
    def sha_for_source_code_file(self, data, **kwargs):
        arch = data.get("architecture")
        if isinstance(arch, raw_nodes.ImportableModule):
            return
        elif isinstance(arch, raw_nodes.ImportableSourceFile):
            sha = data.get("architecture_sha256")
            if sha is None:
                raise ValidationError(
                    "When specifying 'architecture' with a callable from a source file, "
                    "the corresponding 'architecture_sha256' field is required."
                )


class TorchscriptWeightsEntry(_WeightsEntryBase):
    raw_nodes = raw_nodes

    bioimageio_description = "Torchscript weights format"
    weights_format = fields.String(validate=field_validators.Equal("torchscript"), required=True, load_only=True)


WeightsEntry = typing.Union[
    KerasHdf5WeightsEntry,
    OnnxWeightsEntry,
    PytorchStateDictWeightsEntry,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
    TorchscriptWeightsEntry,
]


class RunMode(_BioImageIOSchema):
    name = fields.String(required=True, bioimageio_description="The name of the `run_mode`")
    kwargs = fields.Kwargs()

    @validates("name")
    def warn_on_unrecognized_run_mode(self, value: str):
        if isinstance(value, str):
            self.warn("name", f"Unrecognized run mode '{value}'")


class Model(rdf.schema.RDF):
    raw_nodes = raw_nodes

    class Meta:
        unknown = RAISE
        exclude = ("source",)  # while RDF does have a source field, Model does not

    bioimageio_description = f"""# BioImage.IO Model Resource Description File Specification {get_args(raw_nodes.FormatVersion)[-1]}
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing AI models with pretrained weights.
These fields are typically stored in YAML files which we call Model Resource Description Files or `model RDF`.
The model RDFs can be downloaded or uploaded to the bioimage.io website, produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website).

The model RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
"""
    # todo: sync authors with RDF
    authors = fields.List(
        fields.Nested(rdf.schema.Author()),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description=rdf.schema.RDF.authors_bioimageio_description,
    )

    badges = missing_  # todo: allow badges for Model (RDF has it)
    cite = fields.List(
        fields.Nested(rdf.schema.CiteEntry()),
        required=True,  # todo: unify authors with RDF (optional or required?)
        validate=field_validators.Length(min=1),
        bioimageio_description=rdf.schema.RDF.cite_bioimageio_description,
    )

    documentation = fields.Union(
        [
            fields.URL(),
            fields.RelativeLocalPath(
                validate=field_validators.Attribute(
                    "suffix",
                    field_validators.Equal(
                        ".md", error="{!r} is invalid; expected markdown file with '.md' extension."
                    ),
                )
            ),
        ],
        required=True,
        bioimageio_description="Relative path to file with additional documentation in markdown. This means: 1) only "
        "relative file path is allowed 2) the file must be in markdown format with `.md` file name extension 3) URL is "
        "not allowed. It is recommended to use `README.md` as the documentation name.",
    )

    download_url = missing_  # todo: allow download_url for Model (RDF has it)

    format_version = fields.String(
        validate=field_validators.OneOf(get_args_flat(raw_nodes.FormatVersion)),
        required=True,
        bioimageio_description_order=0,
        bioimageio_description=f"""Version of the BioImage.IO Model Resource Description File Specification used.
This is mandatory, and important for the consumer software to verify before parsing the fields.
The recommended behavior for the implementation is to keep backward compatibility and throw an error if the model yaml
is in an unsupported format version. The current format version described here is
{get_args(raw_nodes.FormatVersion)[-1]}""",
    )

    git_repo = fields.URL(
        bioimageio_description=rdf.schema.RDF.git_repo_bioimageio_description
        + "If the model is contained in a subfolder of a git repository, then a url to the exact folder"
        + "(which contains the configuration yaml file) should be used."
    )

    license = fields.String(
        validate=field_validators.OneOf(LICENSES),
        required=True,
        bioimageio_description=rdf.schema.RDF.license_bioimageio_description,
    )

    name = fields.String(
        required=True,
        bioimageio_description="Name of this model. It should be human-readable and only contain letters, numbers, "
        "`_`, `-` or spaces and not be longer than 64 characters.",
    )

    packaged_by = fields.List(
        fields.Nested(rdf.schema.Author()),
        bioimageio_description=f"The persons that have packaged and uploaded this model. Only needs to be specified if "
        f"different from `authors` in root or any entry in `weights`.",
    )

    parent = fields.Nested(
        ModelParent(),
        bioimageio_description="Parent model from which the trained weights of this model have been derived, e.g. by "
        "finetuning the weights of this model on a different dataset. For format changes of the same trained model "
        "checkpoint, see `weights`.",
    )

    run_mode = fields.Nested(
        RunMode(),
        bioimageio_description="Custom run mode for this model: for more complex prediction procedures like test time "
        "data augmentation that currently cannot be expressed in the specification. "
        "No standard run modes are defined yet.",
    )

    timestamp = fields.DateTime(
        required=True,
        bioimageio_description="Timestamp of the initial creation of this model in [ISO 8601]"
        "(#https://en.wikipedia.org/wiki/ISO_8601) format.",
    )

    weights = fields.Dict(
        fields.String(
            validate=field_validators.OneOf(get_args(raw_nodes.WeightsFormat)),
            required=True,
            bioimageio_description=f"Format of this set of weights. Weight formats can define additional (optional or "
            f"required) fields. See [weight_formats_spec_0_4.md]"
            f"(https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/weight_formats_spec_0_4.md). "
            f"One of: {', '.join(get_args(raw_nodes.WeightsFormat))}",
        ),
        fields.Union([fields.Nested(we()) for we in get_args(WeightsEntry)]),
        required=True,
        bioimageio_description="The weights for this model. Weights can be given for different formats, but should "
        "otherwise be equivalent. The available weight formats determine which consumers can use this model.",
    )

    @pre_load
    def add_weights_format_key_to_weights_entry_value(self, data: dict, many=False, partial=False, **kwargs):
        data = deepcopy(data)  # Schema.validate() calls pre_load methods, thus we should not modify the input data
        if many or partial:
            raise NotImplementedError

        for weights_format, weights_entry in data.get("weights", {}).items():
            if "weights_format" in weights_entry:
                raise ValidationError(f"Got unexpected key 'weights_format' in weights entry {weights_format}")

            weights_entry["weights_format"] = weights_format

        return data

    inputs = fields.List(
        fields.Nested(InputTensor()),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="Describes the input tensors expected by this model.",
    )

    @validates("inputs")
    def no_duplicate_input_tensor_names(self, value: typing.List[raw_nodes.InputTensor]):
        if not isinstance(value, list) or not all(isinstance(v, raw_nodes.InputTensor) for v in value):
            raise ValidationError("Could not check for duplicate input tensor names due to another validation error.")

        names = [t.name for t in value]
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate input tensor names are not allowed.")

    outputs = fields.List(
        fields.Nested(OutputTensor()),
        validate=field_validators.Length(min=1),
        bioimageio_description="Describes the output tensors from this model.",
    )

    @validates("outputs")
    def no_duplicate_output_tensor_names(self, value: typing.List[raw_nodes.OutputTensor]):
        if not isinstance(value, list) or not all(isinstance(v, raw_nodes.OutputTensor) for v in value):
            raise ValidationError("Could not check for duplicate output tensor names due to another validation error.")

        names = [t["name"] if isinstance(t, dict) else t.name for t in value]
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate output tensor names are not allowed.")

    @validates_schema
    def no_duplicate_tensor_names(self, data, **kwargs):
        ipts = data.get("inputs")
        if not isinstance(ipts, list) or not all(isinstance(v, raw_nodes.InputTensor) for v in ipts):
            raise ValidationError("Could not check for duplicate tensor names due to another validation error.")

        outs = data.get("outputs")
        if not isinstance(outs, list) or not all(isinstance(v, raw_nodes.OutputTensor) for v in outs):
            raise ValidationError("Could not check for duplicate tensor names due to another validation error.")

        names = [t.name for t in data["inputs"] + data["outputs"]]
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate tensor names are not allowed.")

    test_inputs = fields.List(
        fields.Union([fields.URI(), fields.RelativeLocalPath()]),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="List of URIs or local relative paths to test inputs as described in inputs for "
        "**a single test case**. "
        "This means if your model has more than one input, you should provide one URI for each input."
        "Each test input should be a file with a ndarray in "
        "[numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format)."
        "The extension must be '.npy'.",
    )
    test_outputs = fields.List(
        fields.Union([fields.URI(), fields.RelativeLocalPath()]),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="Analog to to test_inputs.",
    )

    sample_inputs = fields.List(
        fields.Union([fields.URI(), fields.RelativeLocalPath()]),
        validate=field_validators.Length(min=1),
        bioimageio_description="List of URIs/local relative paths to sample inputs to illustrate possible inputs for "
        "the model, for example stored as png or tif images. "
        "The model is not tested with these sample files that serve to inform a human user about an example use case.",
    )
    sample_outputs = fields.List(
        fields.Union([fields.URI(), fields.RelativeLocalPath()]),
        validate=field_validators.Length(min=1),
        bioimageio_description="List of URIs/local relative paths to sample outputs corresponding to the "
        "`sample_inputs`.",
    )

    config = fields.YamlDict(
        bioimageio_description=rdf.schema.RDF.config_bioimageio_description
        + """

    For example:
    ```yaml
    config:
      # custom config for DeepImageJ, see https://github.com/bioimage-io/configuration/issues/23
      deepimagej:
        model_keys:
          # In principle the tag "SERVING" is used in almost every tf model
          model_tag: tf.saved_model.tag_constants.SERVING
          # Signature definition to call the model. Again "SERVING" is the most general
          signature_definition: tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY
        test_information:
          input_size: [2048x2048] # Size of the input images
          output_size: [1264x1264 ]# Size of all the outputs
          device: cpu # Device used. In principle either cpu or GPU
          memory_peak: 257.7 Mb # Maximum memory consumed by the model in the device
          runtime: 78.8s # Time it took to run the model
          pixel_size: [9.658E-4µmx9.658E-4µm] # Size of the pixels of the input
    ```
"""
    )

    @validates_schema
    def validate_reference_tensor_names(self, data, **kwargs):
        def get_tnames(tname: str):
            return [t.get("name") if isinstance(t, dict) else t.name for t in data.get(tname, [])]

        valid_input_tensor_references = get_tnames("inputs")
        ins = data.get("inputs", [])
        outs = data.get("outputs", [])
        if not isinstance(ins, list) or not isinstance(outs, list):
            raise ValidationError(
                f"Failed to validate reference tensor names due to other validation errors in inputs/outputs."
            )

        for t in outs:
            if not isinstance(t, raw_nodes.OutputTensor):
                raise ValidationError("Failed to validate reference tensor names due to validation errors in outputs")

            if t.postprocessing is missing_:
                continue

            for postpr in t.postprocessing:
                if postpr.kwargs is missing_:
                    continue

                ref_tensor = postpr.kwargs.get("reference_tensor", missing_)
                if ref_tensor is not missing_ and ref_tensor not in valid_input_tensor_references:
                    raise ValidationError(f"{ref_tensor} not found in inputs")

        for t in ins:
            if not isinstance(t, raw_nodes.InputTensor):
                raise ValidationError("Failed to validate reference tensor names due to validation errors in inputs")

            if t.preprocessing is missing_:
                continue

            for prep in t.preprocessing:
                if prep.kwargs is missing_:
                    continue

                ref_tensor = prep.kwargs.get("reference_tensor", missing_)
                if ref_tensor is not missing_ and ref_tensor not in valid_input_tensor_references:
                    raise ValidationError(f"{ref_tensor} not found in inputs")

                if ref_tensor == t.name:
                    raise ValidationError(f"invalid self reference for preprocessing of tensor {t.name}")

    @validates_schema
    def weights_entries_match_weights_formats(self, data, **kwargs):
        weights: typing.Dict[str, WeightsEntry] = data.get("weights", {})
        for weights_format, weights_entry in weights.items():
            if not isinstance(weights_entry, get_args(raw_nodes.WeightsEntry)):
                raise ValidationError("Cannot validate keys in weights field due to other validation errors.")

            if weights_format in ["keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle"]:
                assert isinstance(
                    weights_entry,
                    (
                        raw_nodes.KerasHdf5WeightsEntry,
                        raw_nodes.TensorflowJsWeightsEntry,
                        raw_nodes.TensorflowSavedModelBundleWeightsEntry,
                    ),
                )
                if weights_entry.tensorflow_version is missing_:
                    # todo: raise ValidationError instead?
                    self.warn(f"weights[{weights_format}]", "missing 'tensorflow_version'")

            if weights_format == "onnx":
                assert isinstance(weights_entry, raw_nodes.OnnxWeightsEntry)
                if weights_entry.opset_version is missing_:
                    # todo: raise ValidationError instead?
                    self.warn(f"weights[{weights_format}]", "missing 'opset_version'")
