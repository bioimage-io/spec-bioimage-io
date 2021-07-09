import typing
import warnings
from copy import deepcopy

import stdnum.iso7064.mod_11_2  # todo: remove
from marshmallow import (
    Schema,
    ValidationError,
    missing as missing_,
    post_load,
    pre_dump,
    pre_load,
    validates,
    validates_schema,
)

from bioimageio.spec.shared import LICENSES, field_validators, fields
from bioimageio.spec.shared.common import get_args, get_args_flat
from bioimageio.spec.shared.schema import SharedBioImageIOSchema
from . import raw_nodes


class BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class Author(BioImageIOSchema):
    name = fields.String(required=True, bioimageio_description="Full name.")
    affiliation = fields.String(bioimageio_description="Affiliation.")
    orcid = fields.String(
        validate=[
            field_validators.Length(19),
            lambda oid: all(oid[idx] == "-" for idx in [4, 9, 14]),
            lambda oid: stdnum.iso7064.mod_11_2.is_valid(oid.replace("-", "")),
        ],
        bioimageio_description="[orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id "
        "in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid]("
        "https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier"
        ") as per ISO 7064 11,2.)",
    )


class Badge(BioImageIOSchema):
    bioimageio_description = "Custom badge"
    label = fields.String(required=True, bioimageio_description="e.g. 'Open in Colab'")
    icon = fields.String(bioimageio_description="e.g. 'https://colab.research.google.com/assets/colab-badge.svg'")
    url = fields.URI(
        bioimageio_description="e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'"
    )


class CiteEntry(BioImageIOSchema):
    text = fields.String(required=True)
    doi = fields.String(bioimageio_maybe_required=True)
    url = fields.String(bioimageio_maybe_required=True)

    @validates_schema
    def doi_or_url(self, data, **kwargs):
        if data.get("doi") is None and data.get("url") is None:
            raise ValidationError("doi or url needs to be specified in a citation")


class RunMode(BioImageIOSchema):
    name = fields.String(
        required=True, bioimageio_description="The name of the `run_mode`"
    )  # todo: limit valid run mode names
    kwargs = fields.Kwargs()


class RDF(BioImageIOSchema):
    bioimageio_description = f"""# BioImage.IO Resource Description File Specification {get_args(raw_nodes.ModelFormatVersion)[-1]}
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
"""

    authors_bioimageio_description = (
        "Dictionary of text keys and URI (or a list of URI) values to additional, relevant files. E.g. we can "
        "place a list of URIs under the `files` to list images and other files that this resource depends on."
    )  # todo: shouldn't we package all attachments (or None) and always package certain fields if present?

    attachments = fields.Dict(
        fields.String,
        fields.Union([fields.URI(), fields.List(fields.URI)]),
        bioimageio_maybe_required=True,
        bioimageio_description=authors_bioimageio_description,
    )

    authors = fields.List(
        fields.Union([fields.Nested(Author), fields.String()]),
        bioimageio_description="A list of authors. The authors are the creators of the specifications and the primary "
        "points of contact.",
    )

    badges = fields.List(fields.Nested(Badge), bioimageio_description="a list of badges")

    cite_bioimageio_description = """A citation entry or list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used."""
    cite = fields.Nested(CiteEntry, many=True, required=True, bioimageio_description=cite_bioimageio_description)

    config_bioimageio_description = (
        "A custom configuration field that can contain any keys not present in the RDF spec. "
        "This means you should not store, for example, github repo URL in `config` since we already have the "
        "`git_repo` key defined in the spec.\n"
        "Keys in `config` may be very specific to a tool or consumer software. To avoid conflicted definitions, "
        "it is recommended to wrap configuration into a sub-field named with the specific domain or tool name, "
        """for example:
```yaml
   config:
      bioimage_io:  # here is the domain name
        my_custom_key: 3837283
        another_key:
           nested: value
      imagej:
        macro_dir: /path/to/macro/file
```
"""
        "If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`."
    )
    config = fields.Dict(bioimageio_descriptio=config_bioimageio_description)

    covers = fields.List(
        fields.URI,
        bioimageio_description="A list of cover images provided by either a relative path to the model folder, or a "
        "hyperlink starting with 'https'.Please use an image smaller than 500KB and an aspect ratio width to height "
        "of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.",  # todo: field_validators image format
    )

    description = fields.String(required=True, bioimageio_description="A string containing a brief description.")

    documentation = fields.RelativeLocalPath(
        validate=field_validators.Attribute(
            "suffix",
            field_validators.Equal(".md", error="{!r} is invalid; expected markdown file with '.md' extension."),
        ),
        required=True,
        bioimageio_description="Relative path to file with additional documentation in markdown. This means: 1) only "
        "relative file path is allowed 2) the file must be in markdown format with `.md` file name extension 3) URL is "
        "not allowed. It is recommended to use `README.md` as the documentation name.",
    )

    download_url = fields.String(
        validate=field_validators.URL(schemes=["http", "https"]),
        bioimageio_description="recommended url to the zipped file if applicable",
    )

    format_version = fields.String(
        validate=field_validators.OneOf(get_args(raw_nodes.GeneralFormatVersion)),
        required=True,
        bioimageio_description_order=0,
        bioimageio_description=(
            "Version of the BioImage.IO General Resource Description File Specification used."
            f"The current format version described here is {get_args(raw_nodes.GeneralFormatVersion)[-1]}. "
            "Note: The general RDF format version is not to be confused with the Model RDF format version."
        ),
    )

    git_repo_bioimageio_description = "A url to the git repository, e.g. to Github or Gitlab."
    git_repo = fields.String(
        validate=field_validators.URL(schemes=["http", "https"]), bioimageio_description=git_repo_bioimageio_description
    )

    icon = fields.String(
        bioimageio_description="an icon for the resource"
    )  # todo: limit length? validate=field_validators.Length(max=1)

    license_bioimageio_description = (
        "A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, "
        "`BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send "
        "an Github issue to discuss your intentions with the community."
    )
    license = fields.String(
        # validate=field_validators.OneOf(LICENSES),  # only warn for now (see warn_about_deprecated_spdx_license) todo: enforce in 0.4.0
        bioimageio_description=license_bioimageio_description
    )

    @validates("license")
    def warn_about_deprecated_spdx_license(self, value: str):
        license_info = LICENSES.get(value)
        if license_info is None:
            warnings.warn(f"{value} is not a recognized SPDX license identifier. See https://spdx.org/licenses/")
        elif license_info["isDeprecatedLicenseId"]:
            warnings.warn(f"{license_info['name']} is deprecated")

    links = fields.List(fields.String, bioimageio_description="links to other bioimage.io resources")

    name = fields.String(required=True, bioimageio_description="name of the resource, a human-friendly name")

    source = fields.URI(bioimageio_description="url to the source of the resource")

    tags = fields.List(fields.String, required=True, bioimageio_description="A list of tags.")

    type = fields.String(required=True)

    @validates("type")
    def validate_type(self, value):
        schema_type = self.__class__.__name__.lower()
        if value != schema_type:
            raise ValidationError(f"type must be {schema_type}. Are you using the correct validator?")

    version = fields.StrictVersion(
        bioimageio_description="The version number of the model. The version number format must be a string in "
        "`MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), "
        "e.g. the initial version number should be `0.1.0`."
    )


class SpecWithKwargs(BioImageIOSchema):
    spec: fields.SpecURI
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
    class Binarize(Schema):  # do not inherit from BioImageIOSchema, return only a validated dict, no specific node
        # todo: inherit from a "TransformSchema" that allows generation of docs for pre and postprocessing
        threshold = fields.Float(required=True)

    class Clip(BioImageIOSchema):
        min = fields.Float(required=True)
        max = fields.Float(required=True)

    class ScaleLinear(BioImageIOSchema):
        axes = fields.Axes(required=True, valid_axes="czyx")
        gain = fields.Array(fields.Float(), missing=fields.Float(missing=1.0))  # todo: check if gain match input axes
        offset = fields.Array(
            fields.Float(), missing=fields.Float(missing=0.0)
        )  # todo: check if offset match input axes

        @validates_schema
        def either_gain_or_offset(self, data, **kwargs):
            if data["gain"] == 1.0 and data["offset"] == 0:
                raise ValidationError("Specify gain!=1.0 or offset!=0.0")

    @validates_schema
    def kwargs_match_selected_preprocessing_name(self, data, **kwargs):
        schema_name = "".join(word.title() for word in data["name"].split("_"))

        try:
            schema_class = getattr(self, schema_name)
        except AttributeError as missing_schema_error:
            raise NotImplementedError(
                f"Schema {schema_name} for {data['name']} {self.__class__.__name__.lower()}"
            ) from missing_schema_error

        kwargs_validation_errors = schema_class().validate(data.get("kwargs", {}))
        if kwargs_validation_errors:
            raise ValidationError(f"Invalid `kwargs` for '{data['name']}': {kwargs_validation_errors}")

    class Sigmoid(BioImageIOSchema):
        pass

    class ZeroMeanUnitVariance(BioImageIOSchema):
        mode = fields.ProcMode(required=True)
        axes = fields.Axes(required=True, valid_axes="czyx")
        mean = fields.Array(fields.Float())  # todo: check if means match input axes (for mode 'fixed')
        std = fields.Array(fields.Float())
        eps = fields.Float(missing=1e-6)

        @validates_schema
        def mean_and_std_match_mode(self, data, **kwargs):
            if data["mode"] == "fixed" and ("mean" not in data or "std" not in data):
                raise ValidationError(
                    "`kwargs` for 'zero_mean_unit_variance' preprocessing with `mode` 'fixed' require additional `kwargs`: `mean` and `std`."
                )
            elif data["mode"] != "fixed" and ("mean" in data or "std" in data):
                raise ValidationError(
                    "`kwargs`: `mean` and `std` for 'zero_mean_unit_variance' preprocessing are only valid for `mode` 'fixed'."
                )


class Preprocessing(Processing):
    name = fields.String(
        required=True,
        validate=field_validators.OneOf(get_args(raw_nodes.PreprocessingName)),
        bioimageio_description=f"Name of preprocessing. One of: {', '.join(get_args(raw_nodes.PreprocessingName))} "
        f"(see [supported_formats_and_operations.md#preprocessing](https://github.com/bioimage-io/configuration/"
        f"blob/master/supported_formats_and_operations.md#preprocessing) "
        f"for information on which transformations are supported by specific consumer software).",
    )
    kwargs = fields.Kwargs()

    class ScaleRange(BioImageIOSchema):
        mode = fields.ProcMode(required=True, valid_modes=("per_dataset", "per_sample"))
        axes = fields.Axes(required=True, valid_axes="czyx")
        min_percentile = fields.Float(
            required=True, validate=field_validators.Range(0, 100, min_inclusive=True, max_inclusive=True)
        )
        max_percentile = fields.Float(
            required=True, validate=field_validators.Range(1, 100, min_inclusive=False, max_inclusive=True)
        )  # as a precaution 'max_percentile' needs to be greater than 1

        @validates_schema
        def min_smaller_max(self, data, **kwargs):
            min_p = data["min_percentile"]
            max_p = data["max_percentile"]
            if min_p >= max_p:
                raise ValidationError(f"min_percentile {min_p} >= max_percentile {max_p}")


class Postprocessing(Processing):
    name = fields.String(
        validate=field_validators.OneOf(get_args(raw_nodes.PostprocessingName)),
        required=True,
        bioimageio_description=f"Name of postprocessing. One of: {', '.join(get_args(raw_nodes.PostprocessingName))} "
        f"(see [supported_formats_and_operations.md#postprocessing](https://github.com/bioimage-io/configuration/"
        f"blob/master/supported_formats_and_operations.md#postprocessing) "
        f"for information on which transformations are supported by specific consumer software).",
    )
    kwargs = fields.Kwargs()

    class ScaleRange(Preprocessing.ScaleRange):
        reference_tensor = fields.String(required=True, validate=field_validators.Predicate("isidentifier"))

    class ScaleMeanVariance(BioImageIOSchema):
        mode = fields.ProcMode(required=True, valid_modes=("per_dataset", "per_sample"))
        reference_tensor = fields.String(required=True, validate=field_validators.Predicate("isidentifier"))


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

        if isinstance(shape, raw_nodes.ImplicitInputShape):
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
    weights_format: fields.String
    authors = fields.List(
        fields.Nested(Author),
        bioimageio_description="A list of authors. If this is the root weight (it does not have a `parent` field): the "
        "person(s) that have trained this model. If this is a child weight (it has a `parent` field): the person(s) "
        "who have converted the weights to this format.",
    )  # todo: copy root authors if missing
    attachments = fields.Dict(
        bioimageio_description="Dictionary of text keys and URI (or a list of URI) values to additional, relevant "
        "files that are specific to the current weight format. A list of URIs can be listed under the `files` key to "
        "included additional files for generating the model package."
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
    source = fields.URI(required=True, bioimageio_description="Link to the source file. Preferably a url.")
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
        ensures to serialize a raw_node.<Special>WeightsEntry with the corresponding schema.<Special>WeightsEntry

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
    uri = fields.URI(
        bioimageio_description="Url of another model available on bioimage.io or path to a local model in the "
        "bioimage.io specification. If it is a url, it needs to be a github url linking to the page containing the "
        "model (NOT the raw file)."
    )
    sha256 = fields.SHA256(bioimageio_description="Hash of the weights of the parent model.")


class Model(RDF):
    bioimageio_description = f"""# BioImage.IO Model Resource Description File Specification {get_args(raw_nodes.ModelFormatVersion)[-1]}
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing AI models with pretrained weights.
These fields are typically stored in YAML files which we called Model Resource Description Files or `model RDF`.
The model RDFs can be downloaded or uploaded to the bioimage.io website, produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website).

The model RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
"""
    # todo: unify authors with RDF (optional or required?)
    authors = fields.List(
        fields.Nested(Author), required=True, bioimageio_description=RDF.authors_bioimageio_description
    )

    badges = missing_  # todo: allow badges for Model (RDF has it)
    cite = fields.Nested(
        CiteEntry,
        many=True,
        required=True,  # todo: unify authors with RDF (optional or required?)
        bioimageio_description=RDF.cite_bioimageio_description,
    )

    download_url = missing_  # todo: allow download_url for Model (RDF has it)

    dependencies = fields.Dependencies(  # todo: add validation (0.4.0?)
        bioimageio_description="Dependency manager and dependency file, specified as `<dependency manager>:<relative "
        "path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'"
    )

    format_version = fields.String(
        validate=field_validators.OneOf(get_args_flat(raw_nodes.ModelFormatVersion)),
        required=True,
        bioimageio_description_order=0,
        bioimageio_description=f"""Version of the BioImage.IO Model Resource Description File Specification used.
This is mandatory, and important for the consumer software to verify before parsing the fields.
The recommended behavior for the implementation is to keep backward compatibility and throw an error if the model yaml
is in an unsupported format version. The current format version described here is
{get_args(raw_nodes.ModelFormatVersion)[-1]}""",
    )

    framework = fields.String(
        validate=field_validators.OneOf(get_args(raw_nodes.Framework)),
        bioimageio_description=f"The deep learning framework of the source code. One of: "
        f"{', '.join(get_args(raw_nodes.Framework))}. This field is only required if the field `source` is present.",
    )

    git_repo = fields.String(
        validate=field_validators.URL(schemes=["http", "https"]),
        bioimageio_description=RDF.git_repo_bioimageio_description
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
        bioimageio_description=RDF.license_bioimageio_description,
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
        "data augmentation that currently cannot be expressed in the specification. The different run modes should be "
        "listed in [supported_formats_and_operations.md#Run Modes]"
        "(https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#run-modes).",
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
        fields.URI,
        required=True,
        bioimageio_description="List of URIs to test inputs as described in inputs for a single test case. "
        "Supported file formats/extensions: '.npy'",
    )
    test_outputs = fields.List(fields.URI, required=True, bioimageio_description="Analog to to test_inputs.")

    sample_inputs = fields.List(
        fields.URI,
        bioimageio_description="List of URIs to sample inputs to illustrate possible inputs for the model, for example "
        "stored as png or tif images.",
    )
    sample_outputs = fields.List(
        fields.URI, bioimageio_description="List of URIs to sample outputs corresponding to the `sample_inputs`."
    )

    config = fields.Dict(
        bioimageio_description=RDF.config_bioimageio_description
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


# Collection
class CollectionEntry(BioImageIOSchema):
    """instead of nesting RDFs, RDFs can be pointed to"""

    source = fields.URI(validate=field_validators.URL(schemes=["http", "https"]), required=True)
    id = fields.String(required=True)
    links = fields.List(fields.String())


class ModelCollectionEntry(CollectionEntry):
    download_url = fields.URI(validate=field_validators.URL(schemes=["http", "https"]))


class Collection(RDF):
    application = fields.List(fields.Union([fields.Nested(CollectionEntry), fields.Nested(RDF)]))
    collection = fields.List(fields.Union([fields.Nested(CollectionEntry), fields.Nested(RDF)]))
    model = fields.List(fields.Nested(ModelCollectionEntry))
    dataset = fields.List(fields.Union([fields.Nested(CollectionEntry), fields.Nested(RDF)]))
    notebook = fields.List(fields.Union([fields.Nested(CollectionEntry), fields.Nested(RDF)]))


# deprecated manifest draft:  # todo: remove
class BioImageIoManifestModelEntry(BioImageIOSchema):
    id = fields.String(required=True)
    source = fields.String(validate=field_validators.URL(schemes=["http", "https"]))
    links = fields.List(fields.String)
    download_url = fields.String(validate=field_validators.URL(schemes=["http", "https"]))


class BioImageIoManifestNotebookEntry(BioImageIOSchema):  # todo: remove  # todo: add notebook RDF??
    id = fields.String(required=True)
    name = fields.String(required=True)
    documentation = fields.RelativeLocalPath(
        required=True,
        validate=field_validators.Attribute(
            "suffix",
            field_validators.Equal(".md", error="{!r} is invalid; expected markdown file with '.md' extension."),
        ),
    )
    description = fields.String(required=True)

    cite = fields.List(fields.Nested(CiteEntry))
    authors = fields.List(fields.Nested(Author), required=True)
    covers = fields.List(fields.URI)

    badges = fields.List(fields.Nested(Badge))
    tags = fields.List(fields.String)
    source = fields.URI(required=True)
    links = fields.List(fields.String)  # todo: make List[URI]?


class BioImageIoManifest(BioImageIOSchema):  # todo: remove
    format_version = fields.String(
        validate=field_validators.OneOf(get_args(raw_nodes.GeneralFormatVersion)), required=True
    )
    config = fields.Dict()

    application = fields.List(fields.Dict)
    collection = fields.List(fields.Dict)
    model = fields.List(fields.Nested(BioImageIoManifestModelEntry))
    dataset = fields.List(fields.Dict)
    notebook = fields.List(fields.Nested(BioImageIoManifestNotebookEntry))
