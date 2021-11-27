import typing
import warnings
from copy import deepcopy

from marshmallow import RAISE, ValidationError, missing as missing_, post_load, pre_dump, pre_load, validates_schema

from bioimageio.spec.rdf import v0_2 as rdf
from bioimageio.spec.shared import field_validators, fields
from bioimageio.spec.shared.common import get_args, get_args_flat
from bioimageio.spec.shared.schema import SharedBioImageIOSchema, SharedProcessingSchema
from . import raw_nodes

Author = rdf.schema.Author
CiteEntry = rdf.schema.CiteEntry


class BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class RunMode(BioImageIOSchema):
    name = fields.String(
        required=True, bioimageio_description="The name of the `run_mode`"
    )  # todo: limit valid run mode names
    kwargs = fields.Kwargs()


class Tensor(BioImageIOSchema):
    name = fields.String(
        required=True, validate=field_validators.Predicate("isidentifier"), bioimageio_description="Tensor name."
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
        axes = data["axes"]
        processing_list = data.get(self.processing_name, [])
        for processing in processing_list:
            name = processing.name
            kwargs = processing.kwargs or {}
            kwarg_axes = kwargs.get("axes", "")
            if any(a not in axes for a in kwarg_axes):
                raise ValidationError("`kwargs.axes` needs to be subset of axes")


class Processing(BioImageIOSchema):
    class binarize(SharedProcessingSchema):
        bioimageio_description = (
            "Binarize the tensor with a fixed threshold, values above the threshold will be set to one, values below "
            "the threshold to zero."
        )
        threshold = fields.Float(required=True, bioimageio_description="The fixed threshold")

    class clip(SharedProcessingSchema):
        bioimageio_description = "Set tensor values below min to min and above max to max."
        min = fields.Float(required=True, bioimageio_description="minimum value for clipping")
        max = fields.Float(required=True, bioimageio_description="maximum value for clipping")

    class scale_linear(SharedProcessingSchema):
        bioimageio_description = "Fixed linear scaling."
        axes = fields.Axes(
            required=True,
            valid_axes="czyx",
            bioimageio_description="The subset of axes to scale jointly. "
            "For example xy to scale the two image axes for 2d data jointly. "
            "The batch axis (b) is not valid here.",
        )
        gain = fields.Array(
            fields.Float(), missing=fields.Float(missing=1.0), bioimageio_description="multiplicative factor"
        )  # todo: check if gain match input axes
        offset = fields.Array(
            fields.Float(), missing=fields.Float(missing=0.0), bioimageio_description="additive term"
        )  # todo: check if offset match input axes

        @validates_schema
        def either_gain_or_offset(self, data, **kwargs):
            gain = data["gain"]
            if isinstance(gain, (float, int)):
                gain = [gain]

            offset = data["offset"]
            if isinstance(offset, (float, int)):
                offset = [offset]

            if all(g == 1.0 for g in gain) and all(off == 0 for off in offset):
                raise ValidationError("Specify gain!=1.0 or offset!=0.0")

    @validates_schema
    def kwargs_match_selected_preprocessing_name(self, data, **kwargs):
        schema_name = data["name"]

        try:
            schema_class = getattr(self, schema_name)
        except AttributeError as missing_schema_error:
            raise NotImplementedError(
                f"Schema {schema_name} for {data['name']} {self.__class__.__name__.lower()}"
            ) from missing_schema_error

        kwargs_validation_errors = schema_class().validate(data.get("kwargs", {}))
        if kwargs_validation_errors:
            raise ValidationError(f"Invalid `kwargs` for '{data['name']}': {kwargs_validation_errors}")

    class sigmoid(SharedProcessingSchema):
        bioimageio_description = ""

    class zero_mean_unit_variance(SharedProcessingSchema):
        bioimageio_description = "Subtract mean and divide by variance."
        mode = fields.ProcMode(required=True)
        axes = fields.Axes(
            required=True,
            valid_axes="czyx",
            bioimageio_description="The subset of axes to normalize jointly. For example xy to normalize the two image "
            "axes for 2d data jointly. The batch axis (b) is not valid here.",
        )
        mean = fields.Array(
            fields.Float(),
            bioimageio_description="The mean value(s) to use for `mode == fixed`. For example `[1.1, 2.2, 3.3]` in the "
            "case of a 3 channel image where the channels are not normalized jointly.",
        )  # todo: check if means match input axes (for mode 'fixed')
        std = fields.Array(
            fields.Float(),
            bioimageio_description="The standard deviation values to use for `mode == fixed`. Analogous to mean.",
        )
        eps = fields.Float(
            missing=1e-6,
            bioimageio_description="epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`. "
            "Default value: 10^-6.",
        )

        @validates_schema
        def mean_and_std_match_mode(self, data, **kwargs):
            if data["mode"] == "fixed" and ("mean" not in data or "std" not in data):
                raise ValidationError(
                    "`kwargs` for 'zero_mean_unit_variance' preprocessing with `mode` 'fixed' require additional "
                    "`kwargs`: `mean` and `std`."
                )
            elif data["mode"] != "fixed" and ("mean" in data or "std" in data):
                raise ValidationError(
                    "`kwargs`: `mean` and `std` for 'zero_mean_unit_variance' preprocessing are only valid for `mode` 'fixed'."
                )


class Preprocessing(Processing):
    name = fields.String(
        required=True,
        validate=field_validators.OneOf(get_args(raw_nodes.PreprocessingName)),
        bioimageio_description=f"Name of preprocessing. One of: {', '.join(get_args(raw_nodes.PreprocessingName))}.",
    )
    kwargs = fields.Kwargs(
        bioimageio_description=f"Key word arguments as described in [preprocessing spec]"
        f"(https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/preprocessing_spec_"
        f"{'_'.join(get_args(raw_nodes.FormatVersion)[-1].split('.')[:2])}.md)."
    )

    class scale_range(SharedProcessingSchema):
        bioimageio_description = "Scale with percentiles."
        mode = fields.ProcMode(required=True, valid_modes=("per_dataset", "per_sample"))
        axes = fields.Axes(
            required=True,
            valid_axes="czyx",
            bioimageio_description="The subset of axes to normalize jointly. For example xy to normalize the two image "
            "axes for 2d data jointly. The batch axis (b) is not valid here.",
        )
        min_percentile = fields.Float(
            default=0,
            validate=field_validators.Range(0, 100, min_inclusive=True, max_inclusive=False),
            bioimageio_description="The lower percentile used for normalization, in range 0 to 100. Default value: 0.",
        )
        max_percentile = fields.Float(
            default=100,
            validate=field_validators.Range(1, 100, min_inclusive=False, max_inclusive=True),
            bioimageio_description="The upper percentile used for normalization, in range 1 to 100. Has to be bigger "
            "than min_percentile. Default value: 100. The range is 1 to 100 instead of 0 to 100 to avoid mistakenly "
            "accepting percentiles specified in the range 0.0 to 1.0.",
        )
        eps = fields.Float(
            missing=1e-6,
            bioimageio_description="Epsilon for numeric stability: "
            "`out = (tensor - v_lower) / (v_upper - v_lower + eps)`; "
            "with `v_lower,v_upper` values at the respective percentiles. Default value: 10^-6.",
        )

        @validates_schema
        def min_smaller_max(self, data, **kwargs):
            min_p = data.get("min_percentile", 0)
            max_p = data.get("max_percentile", 100)
            if min_p >= max_p:
                raise ValidationError(f"min_percentile {min_p} >= max_percentile {max_p}")


class Postprocessing(Processing):
    name = fields.String(
        validate=field_validators.OneOf(get_args(raw_nodes.PostprocessingName)),
        required=True,
        bioimageio_description=f"Name of postprocessing. One of: {', '.join(get_args(raw_nodes.PostprocessingName))}.",
    )
    kwargs = fields.Kwargs(
        bioimageio_description=f"Key word arguments as described in [postprocessing spec]"
        f"(https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/postprocessing_spec_"
        f"{'_'.join(get_args(raw_nodes.FormatVersion)[-1].split('.')[:2])}.md)."
    )

    class scale_range(Preprocessing.scale_range):
        reference_tensor = fields.String(
            required=False,
            validate=field_validators.Predicate("isidentifier"),
            bioimageio_description="Tensor name to compute the percentiles from. Default: The tensor itself. "
            "If mode==per_dataset this needs to be the name of an input tensor.",
        )

    class scale_mean_variance(SharedProcessingSchema):
        bioimageio_description = "Scale the tensor s.t. its mean and variance match a reference tensor."
        mode = fields.ProcMode(required=True, valid_modes=("per_dataset", "per_sample"))
        reference_tensor = fields.String(
            required=True,
            validate=field_validators.Predicate("isidentifier"),
            bioimageio_description="Name of tensor to match.",
        )


class InputTensor(Tensor):
    shape = fields.InputShape(required=True, bioimageio_description="Specification of tensor shape.")
    preprocessing = fields.List(
        fields.Nested(Preprocessing), bioimageio_description="Description of how this input should be preprocessed."
    )
    processing_name = "preprocessing"

    @validates_schema
    def zero_batch_step_and_one_batch_size(self, data, **kwargs):
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


class OutputTensor(Tensor):
    shape = fields.OutputShape(required=True)
    halo = fields.List(
        fields.Integer,
        bioimageio_description="The halo to crop from the output tensor (for example to crop away boundary effects or "
        "for tiling). The halo should be cropped from both sides, i.e. `shape_after_crop = shape - 2 * halo`. The "
        "`halo` is not cropped by the bioimage.io model, but is left to be cropped by the consumer software. Use "
        "`shape:offset` if the model output itself is cropped and input and output shapes not fixed.",
    )
    postprocessing = fields.List(
        fields.Nested(Postprocessing), bioimageio_description="Description of how this output should be postprocessed."
    )
    processing_name = "postprocessing"

    @validates_schema
    def matching_halo_length(self, data, **kwargs):
        shape = data["shape"]
        halo = data.get("halo")
        if halo is None:
            return
        elif isinstance(shape, list) or isinstance(shape, raw_nodes.ImplicitOutputShape):
            if len(halo) != len(shape):
                raise ValidationError(f"halo {halo} has to have same length as shape {shape}!")
        else:
            raise NotImplementedError(type(shape))


_common_sha256_hint = (
    "You can drag and drop your file to this [online tool]"
    "(http://emn178.github.io/online-tools/sha256_checksum.html) to generate it in your browser. "
    "Or you can generate the SHA256 code for your model and weights by using for example, `hashlib` in Python. "
    # "[here is a codesnippet](#code-snippet-to-compute-sha256-checksum)."  # todo: link to code snippet and don't multiply it
    + """
    Code snippet to compute SHA256 checksum
    
    ```python
    import hashlib
    
    filename = "your filename here"
    with open(filename, "rb") as f:
      bytes = f.read() # read entire file as bytes
      readable_hash = hashlib.sha256(bytes).hexdigest()
      print(readable_hash)
      ```

"""
)


class WeightsEntryBase(BioImageIOSchema):
    authors = fields.List(
        fields.Nested(Author),
        bioimageio_description="A list of authors. If this is the root weight (it does not have a `parent` field): the "
        "person(s) that have trained this model. If this is a child weight (it has a `parent` field): the person(s) "
        "who have converted the weights to this format.",
    )  # todo: copy root authors if missing
    attachments = fields.Dict(
        fields.String,
        fields.List(fields.Union([fields.URI(), fields.Raw()])),
        bioimageio_description="Dictionary of text keys and list values (that may contain any valid yaml) to "
        "additional, relevant files that are specific to the current weight format. A list of URIs can be listed under"
        " the `files` key to included additional files for generating the model package.",
    )
    parent = fields.String(
        bioimageio_description="The source weights used as input for converting the weights to this format. For "
        "example, if the weights were converted from the format `pytorch_state_dict` to `pytorch_script`, the parent "
        "is `pytorch_state_dict`. All weight entries except one (the initial set of weights resulting from training "
        "the model), need to have this field."
    )
    sha256 = fields.String(
        validate=field_validators.Length(equal=64),
        bioimageio_description="SHA256 checksum of the source file specified. " + _common_sha256_hint,
    )
    source = fields.Union(
        [fields.URI(), fields.RelativeLocalPath()],
        required=True,
        bioimageio_description="URI or path to the weights file. Preferably a url.",
    )
    weights_format = fields.String(
        validate=field_validators.OneOf(get_args(raw_nodes.WeightsFormat)), required=True, load_only=True
    )

    @post_load
    def make_object(self, data, **kwargs):
        data.pop("weights_format")  # weights_format was only used to identify correct WeightsEntry schema
        return super().make_object(data, **kwargs)

    @pre_dump
    def raise_on_weights_format_mismatch(self, raw_node, **kwargs):
        """
        ensures to serialize a raw_nodes.<Special>WeightsEntry with the corresponding schema.<Special>WeightsEntry

        This check is required, because no validation is performed by marshmallow on serialization,
        which disables the Union field to select the appropriate nested schema for serialization.
        """
        if self.__class__.__name__ != raw_node.__class__.__name__:
            raise TypeError(f"Cannot serialize {raw_node} with {self}")

        return raw_node


class KerasHdf5WeightsEntry(WeightsEntryBase):
    bioimageio_description = "Keras HDF5 weights format"
    weights_format = fields.String(validate=field_validators.Equal("keras_hdf5"), required=True, load_only=True)
    tensorflow_version = fields.StrictVersion()  # todo: required=True


class OnnxWeightsEntry(WeightsEntryBase):
    bioimageio_description = "ONNX weights format"
    weights_format = fields.String(validate=field_validators.Equal("onnx"), required=True, load_only=True)
    opset_version = fields.Integer()  # todo: required=True


class PytorchStateDictWeightsEntry(WeightsEntryBase):
    bioimageio_description = "PyTorch state dictionary weights format"
    weights_format = fields.String(validate=field_validators.Equal("pytorch_state_dict"), required=True, load_only=True)


class PytorchScriptWeightsEntry(WeightsEntryBase):
    bioimageio_description = "Torch Script weights format"
    weights_format = fields.String(validate=field_validators.Equal("pytorch_script"), required=True, load_only=True)


class TensorflowJsWeightsEntry(WeightsEntryBase):
    bioimageio_description = "Tensorflow Javascript weights format"
    weights_format = fields.String(validate=field_validators.Equal("tensorflow_js"), required=True, load_only=True)
    tensorflow_version = fields.StrictVersion()  # todo: required=True


class TensorflowSavedModelBundleWeightsEntry(WeightsEntryBase):
    bioimageio_description = "Tensorflow Saved Model Bundle weights format"
    weights_format = fields.String(
        validate=field_validators.Equal("tensorflow_saved_model_bundle"), required=True, load_only=True
    )
    tensorflow_version = fields.StrictVersion()  # todo: required=True


WeightsEntry = typing.Union[
    PytorchStateDictWeightsEntry,
    PytorchScriptWeightsEntry,
    KerasHdf5WeightsEntry,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
    OnnxWeightsEntry,
]


class ModelParent(BioImageIOSchema):
    uri = fields.Union(  # todo: allow URI or DOI instead (and not local path!?)
        [fields.URI(), fields.RelativeLocalPath()],
        bioimageio_description="Url of another model available on bioimage.io or path to a local model in the "
        "bioimage.io specification. If it is a url, it needs to be a github url linking to the page containing the "
        "model (NOT the raw file).",
    )
    sha256 = fields.SHA256(bioimageio_description="Hash of the weights of the parent model.")


class Model(rdf.schema.RDF):
    raw_nodes = raw_nodes

    class Meta:
        unknown = RAISE

    bioimageio_description = f"""# BioImage.IO Model Resource Description File Specification {get_args(raw_nodes.FormatVersion)[-1]}
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing AI models with pretrained weights.
These fields are typically stored in YAML files which we called Model Resource Description Files or `model RDF`.
The model RDFs can be downloaded or uploaded to the bioimage.io website, produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website).

The model RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
"""
    # todo: unify authors with RDF (optional or required?)
    authors = fields.List(
        fields.Nested(Author), required=True, bioimageio_description=rdf.schema.RDF.authors_bioimageio_description
    )

    badges = missing_  # todo: allow badges for Model (RDF has it)
    cite = fields.Nested(
        CiteEntry,
        many=True,
        required=True,  # todo: unify authors with RDF (optional or required?)
        bioimageio_description=rdf.schema.RDF.cite_bioimageio_description,
    )

    download_url = missing_  # todo: allow download_url for Model (RDF has it)

    dependencies = fields.Dependencies(  # todo: add validation (0.4.0?)
        bioimageio_description="Dependency manager and dependency file, specified as `<dependency manager>:<relative "
        "path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'"
    )

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

    framework = fields.String(
        validate=field_validators.OneOf(get_args(raw_nodes.Framework)),
        bioimageio_description=f"The deep learning framework of the source code. One of: "
        f"{', '.join(get_args(raw_nodes.Framework))}. This field is only required if the field `source` is present.",
    )

    git_repo = fields.String(
        validate=field_validators.URL(schemes=["http", "https"]),
        bioimageio_description=rdf.schema.RDF.git_repo_bioimageio_description
        + "If the model is contained in a subfolder of a git repository, then a url to the exact folder"
        + "(which contains the configuration yaml file) should be used.",
    )

    icon = missing_  # todo: allow icon for Model (RDF has it)

    kwargs = fields.Kwargs(
        bioimageio_description="Keyword arguments for the implementation specified by `source`. "
        "This field is only required if the field `source` is present."
    )

    language = fields.String(
        validate=field_validators.OneOf(get_args(raw_nodes.Language)),
        bioimageio_maybe_required=True,
        bioimageio_description=f"Programming language of the source code. One of: "
        f"{', '.join(get_args(raw_nodes.Language))}. This field is only required if the field `source` is present.",
    )

    license = fields.String(
        required=True,  # todo: unify license with RDF (optional or required?)
        bioimageio_description=rdf.schema.RDF.license_bioimageio_description,
    )

    name = fields.String(
        # validate=field_validators.Length(max=36),  # todo: enforce in future version (0.4.0?)
        required=True,
        bioimageio_description="Name of this model. It should be human-readable and only contain letters, numbers, "
        "`_`, `-` or spaces and not be longer than 36 characters.",
    )

    packaged_by = fields.List(
        fields.Nested(Author),
        bioimageio_description=f"The persons that have packaged and uploaded this model. Only needs to be specified if "
        f"different from `authors` in root or any entry in `weights`.",
    )

    parent = fields.Nested(
        ModelParent,
        bioimageio_description="Parent model from which the trained weights of this model have been derived, e.g. by "
        "finetuning the weights of this model on a different dataset. For format changes of the same trained model "
        "checkpoint, see `weights`.",
    )

    run_mode = fields.Nested(
        RunMode,
        bioimageio_description="Custom run mode for this model: for more complex prediction procedures like test time "
        "data augmentation that currently cannot be expressed in the specification. "
        "No standard run modes are defined yet.",
    )

    sha256 = fields.String(
        validate=field_validators.Length(equal=64),
        bioimageio_description="SHA256 checksum of the model source code file."
        + _common_sha256_hint
        + " This field is only required if the field source is present.",
    )

    source = fields.ImportableSource(
        bioimageio_maybe_required=True,
        bioimageio_description="Language and framework specific implementation. As some weights contain the model "
        "architecture, the source is optional depending on the present weight formats. `source` can either point to a "
        "local implementation: `<relative path to file>:<identifier of implementation within the source file>` or the "
        "implementation in an available dependency: `<root-dependency>.<sub-dependency>.<identifier>`.\nFor example: "
        "`my_function.py:MyImplementation` or `core_library.some_module.some_function`.",
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
            f"required) fields. See [supported_formats_and_operations.md#Weight Format]"
            f"(https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#weight_format). "
            f"One of: {', '.join(get_args(raw_nodes.WeightsFormat))}",
        ),
        fields.Union([fields.Nested(we) for we in get_args(WeightsEntry)]),
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

    inputs = fields.Nested(
        InputTensor, many=True, bioimageio_description="Describes the input tensors expected by this model."
    )
    outputs = fields.Nested(
        OutputTensor, many=True, bioimageio_description="Describes the output tensors from this model."
    )

    test_inputs = fields.List(
        fields.Union([fields.URI(), fields.RelativeLocalPath()]),
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
        required=True,
        bioimageio_description="Analog to to test_inputs.",
    )

    sample_inputs = fields.List(
        fields.Union([fields.URI(), fields.RelativeLocalPath()]),
        bioimageio_description="List of URIs/local relative paths to sample inputs to illustrate possible inputs for "
        "the model, for example stored as png or tif images. "
        "The model is not tested with these sample files that serve to inform a human user about an example use case.",
    )
    sample_outputs = fields.List(
        fields.Union([fields.URI(), fields.RelativeLocalPath()]),
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
    def language_and_framework_match(self, data, **kwargs):
        field_names = ("language", "framework")
        valid_combinations = [
            ("python", "scikit-learn"),  # todo: remove
            ("python", "pytorch"),
            ("python", "tensorflow"),
            ("java", "tensorflow"),
        ]
        if "source" not in data:
            valid_combinations.append((missing_, missing_))
            valid_combinations.append(("python", missing_))
            valid_combinations.append(("java", missing_))

        combination = tuple(data.get(name, missing_) for name in field_names)
        if combination not in valid_combinations:
            raise ValidationError(f"invalid combination of {dict(zip(field_names, combination))}")

    @validates_schema
    def source_specified_if_required(self, data, **kwargs):
        if "source" in data:
            return

        weights_format_requires_source = {
            "pytorch_state_dict": True,
            "pytorch_script": False,
            "keras_hdf5": False,
            "tensorflow_js": False,
            "tensorflow_saved_model_bundle": False,
            "onnx": False,
        }
        require_source = {wf for wf in data["weights"] if weights_format_requires_source[wf]}
        if require_source:
            raise ValidationError(
                f"These specified weight formats require source code to be specified: {require_source}"
            )

    @validates_schema
    def validate_reference_tensor_names(self, data, **kwargs):
        valid_input_tensor_references = [ipt.name for ipt in data["inputs"]]
        for out in data["outputs"]:
            if out.postprocessing is missing_:
                continue

            for postpr in out.postprocessing:
                if postpr.kwargs is missing_:
                    continue

                ref_tensor = postpr.kwargs.get("reference_tensor", missing_)
                if ref_tensor is not missing_ and ref_tensor not in valid_input_tensor_references:
                    raise ValidationError(f"{ref_tensor} not found in inputs")

    @validates_schema
    def weights_entries_match_weights_formats(self, data, **kwargs):
        weights: typing.Dict[str, WeightsEntryBase] = data["weights"]
        for weights_format, weights_entry in weights.items():
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
                    # todo: raise ValidationError (allow -> require)?
                    warnings.warn(f"missing 'tensorflow_version' entry for weights format {weights_format}")

            if weights_format == "onnx":
                assert isinstance(weights_entry, raw_nodes.OnnxWeightsEntry)
                if weights_entry.opset_version is missing_:
                    # todo: raise ValidationError?
                    warnings.warn(f"missing 'opset_version' entry for weights format {weights_format}")
