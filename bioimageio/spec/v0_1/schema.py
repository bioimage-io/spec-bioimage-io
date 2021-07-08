from marshmallow import ValidationError, validates_schema

from bioimageio.spec.shared import fields
from bioimageio.spec.shared.schema import ImplicitInputShape, ImplicitOutputShape, SharedBioImageIOSchema
from . import raw_nodes


class BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class CiteEntry(BioImageIOSchema):
    text = fields.String(required=True)
    doi = fields.String()
    url = fields.String()

    @validates_schema
    def doi_or_url(self, data, **kwargs):
        if "doi" not in data and "url" not in data:
            raise ValidationError("doi or url needs to be specified in a citation")


class BaseSpec(BioImageIOSchema):
    name = fields.String(required=True)
    format_version = fields.String(required=True)
    description = fields.String(required=True)
    cite = fields.Nested(CiteEntry(many=True), required=True)
    authors = fields.List(fields.String(required=True))
    documentation = fields.RelativeLocalPath(required=True)
    tags = fields.List(fields.String, required=True)
    license = fields.String(required=True)

    language = fields.String(required=True)
    framework = fields.String()
    source = fields.String(required=True)
    required_kwargs = fields.List(fields.String)
    optional_kwargs = fields.Dict(fields.String)

    test_input = fields.RelativeLocalPath()
    test_output = fields.RelativeLocalPath()
    covers = fields.List(fields.RelativeLocalPath)


class SpecWithKwargs(BioImageIOSchema):
    spec: fields.SpecURI
    kwargs = fields.Dict()


class Array(BioImageIOSchema):
    name = fields.String(required=True)
    axes = fields.Axes()
    data_type = fields.String(required=True)
    data_range = fields.Tuple((fields.Float(allow_nan=True), fields.Float(allow_nan=True)))

    shape: fields.Union


class InputArray(Array):
    shape = fields.Union([fields.ExplicitShape(), fields.Nested(ImplicitInputShape)], required=True)


class OutputArray(Array):
    shape = fields.Union([fields.ExplicitShape(), fields.Nested(ImplicitOutputShape)], required=True)
    halo = fields.List(fields.Integer)


class TransformationSpec(BaseSpec):
    dependencies = fields.Dependencies(required=True)
    inputs = fields.Nested(InputArray, required=True)
    outputs = fields.Nested(OutputArray, required=True)


class Transformation(SpecWithKwargs):
    spec = fields.SpecURI(TransformationSpec, required=True)


class Weights(BioImageIOSchema):
    source = fields.URI(required=True)
    hash = fields.Dict()


class Prediction(BioImageIOSchema):
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


class Optimizer(BioImageIOSchema):
    source = fields.String(required=True)
    required_kwargs = fields.List(fields.String)
    optional_kwargs = fields.Dict(fields.String)


class Setup(BioImageIOSchema):
    samplers = fields.List(fields.Nested(Sampler, required=True), required=True)
    preprocess = fields.Nested(Transformation, many=True)
    postprocess = fields.Nested(Transformation, many=True)
    losses = fields.Nested(Transformation, many=True)
    optimizer = fields.Nested(Optimizer)


class Model(BaseSpec):
    prediction = fields.Nested(Prediction, required=True)
    inputs = fields.Nested(InputArray, many=True, required=True)
    outputs = fields.Nested(OutputArray, many=True, required=True)
    training = fields.Dict()

    config = fields.Dict()
