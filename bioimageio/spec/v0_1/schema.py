from marshmallow import Schema, ValidationError, validates_schema

from bioimageio.spec.shared import fields


class PyBioSchema(Schema):
    bioimageio_description: str = ""


class CiteEntry(PyBioSchema):
    text = fields.String(required=True)
    doi = fields.String()
    url = fields.String()

    @validates_schema
    def doi_or_url(self, data, **kwargs):
        if "doi" not in data and "url" not in data:
            raise ValidationError("doi or url needs to be specified in a citation")


class BaseSpec(PyBioSchema):
    name = fields.String(required=True)
    format_version = fields.String(required=True)
    description = fields.String(required=True)
    cite = fields.Nested(CiteEntry(many=True), required=True)
    authors = fields.List(fields.String(required=True))
    documentation = fields.Path(required=True)
    tags = fields.List(fields.String, required=True)
    license = fields.String(required=True)

    language = fields.String(required=True)
    framework = fields.String()
    source = fields.String(required=True)
    required_kwargs = fields.List(fields.String)
    optional_kwargs = fields.Dict(fields.String)

    test_input = fields.Path()
    test_output = fields.Path()
    covers = fields.List(fields.Path)


class SpecWithKwargs(PyBioSchema):
    spec: fields.SpecURI
    kwargs = fields.Dict()


class InputShape(PyBioSchema):
    min = fields.List(fields.Integer, required=True)
    step = fields.List(fields.Integer, required=True)

    @validates_schema
    def matching_lengths(self, data, **kwargs):
        min_ = data["min"]
        step = data["step"]
        if min_ is None or step is None:
            return

        if len(min_) != len(step):
            raise ValidationError(f"'min' and 'step' have to have the same length! (min: {min_}, step: {step})")


class OutputShape(PyBioSchema):
    reference_input = fields.String()
    scale = fields.List(fields.Float, required=True)
    offset = fields.List(fields.Integer, required=True)

    @validates_schema
    def matching_lengths(self, data, **kwargs):
        scale = data["scale"]
        offset = data["offset"]
        if len(scale) != len(offset):
            raise ValidationError(f"scale {scale} has to have same length as offset {offset}!")


class Array(PyBioSchema):
    name = fields.String(required=True)
    axes = fields.Axes()
    data_type = fields.String(required=True)
    data_range = fields.Tuple((fields.Float(allow_nan=True), fields.Float(allow_nan=True)))

    shape: fields.Nested


class InputArray(Array):
    shape = fields.Union([fields.ExplicitShape(), fields.Nested(InputShape)], required=True)


class OutputArray(Array):
    shape = fields.Union([fields.ExplicitShape(), fields.Nested(OutputShape)], required=True)
    halo = fields.List(fields.Integer)


class TransformationSpec(BaseSpec):
    dependencies = fields.Dependencies(required=True)
    inputs = fields.Nested(InputArray, required=True)
    outputs = fields.Nested(OutputArray, required=True)


class Transformation(SpecWithKwargs):
    spec = fields.SpecURI(TransformationSpec, required=True)


class Weights(PyBioSchema):
    source = fields.URI(required=True)
    hash = fields.Dict()


class Prediction(PyBioSchema):
    weights = fields.Nested(Weights)
    dependencies = fields.Dependencies()
    preprocess = fields.Nested(Transformation, many=True)
    postprocess = fields.Nested(Transformation, many=True)


class ReaderSpec(BaseSpec):
    dependencies = fields.Dependencies()
    outputs = fields.Nested(OutputArray, required=True)


class Reader(SpecWithKwargs):
    spec = fields.SpecURI(ReaderSpec)
    transformations = fields.List(fields.Nested(Transformation))


class SamplerSpec(BaseSpec):
    dependencies = fields.Dependencies()
    outputs = fields.Nested(OutputArray)


class Sampler(SpecWithKwargs):
    spec = fields.SpecURI(SamplerSpec)
    readers = fields.List(fields.Nested(Reader, required=True), required=True)


class Optimizer(PyBioSchema):
    source = fields.String(required=True)
    required_kwargs = fields.List(fields.String)
    optional_kwargs = fields.Dict(fields.String)


class Setup(PyBioSchema):
    samplers = fields.List(fields.Nested(Sampler, required=True), required=True)
    preprocess = fields.Nested(Transformation, many=True)
    postprocess = fields.Nested(Transformation, many=True)
    losses = fields.Nested(Transformation, many=True)
    optimizer = fields.Nested(Optimizer)


class Model(BaseSpec):
    prediction = fields.Nested(Prediction)
    inputs = fields.Nested(InputArray, many=True)
    outputs = fields.Nested(OutputArray, many=True)
    training = fields.Dict()

    config = fields.Dict()
