import typing

from marshmallow import ValidationError, validates, validates_schema

from bioimageio.spec.rdf.v0_2.schema import RDF
from bioimageio.spec.shared import field_validators, fields
from bioimageio.spec.shared.schema import SharedBioImageIOSchema
from . import raw_nodes

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore


class _BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class Tensor(_BioImageIOSchema):
    name = fields.String(
        required=True,
        validate=field_validators.Predicate("isidentifier"),
        bioimageio_description="Tensor name. No duplicates are allowed.",
    )
    description = fields.String()


class Step(_BioImageIOSchema):
    id = fields.String(
        required=False,
        validate=field_validators.Predicate("isidentifier"),
        bioimageio_description="Step id for referencing the steps' kwargs or outputs.",
    )
    op = fields.String(
        required=True,
        validate=field_validators.Predicate("isidentifier"),
        bioimageio_description="Name of operation. Must be implemented in bioimageio.core or bioimageio.contrib.",
    )
    inputs = fields.List(
        fields.String(
            validate=field_validators.Predicate("isidentifier"),
            bioimageio_description="named output of a previous step with the pattern '<step id>.outputs.<output name>'",
        ),
        required=False,
    )
    outputs = fields.List(
        fields.String(
            validate=field_validators.Predicate("isidentifier"),
        ),
        bioimageio_description="output names for this step",
        required=False,
    )
    kwargs = fields.Kwargs(bioimageio_description="Key word arguments for op.")


class Workflow(_BioImageIOSchema, RDF):
    bioimageio_description = f"""# BioImage.IO Workflow Resource Description File {get_args(raw_nodes.FormatVersion)[-1]}
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing workflows.
These fields are typically stored in a YAML file which we call Workflow Resource Description File or `workflow RDF`.

The workflow RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
"""
    inputs = fields.List(
        fields.Nested(Tensor()),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="Describes the input tensors expected by this model.",
    )

    @validates("inputs")
    def no_duplicate_input_tensor_names(self, value: typing.List[raw_nodes.Tensor]):
        if not isinstance(value, list) or not all(isinstance(v, raw_nodes.Tensor) for v in value):
            raise ValidationError("Could not check for duplicate input tensor names due to another validation error.")

        names = [t.name for t in value]
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate input tensor names are not allowed.")

    outputs = fields.List(
        fields.Nested(Tensor()),
        validate=field_validators.Length(min=1),
        bioimageio_description="Describes the output tensors from this model.",
    )

    @validates("outputs")
    def no_duplicate_output_tensor_names(self, value: typing.List[raw_nodes.Tensor]):
        if not isinstance(value, list) or not all(isinstance(v, raw_nodes.Tensor) for v in value):
            raise ValidationError("Could not check for duplicate output tensor names due to another validation error.")

        names = [t["name"] if isinstance(t, dict) else t.name for t in value]
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate output tensor names are not allowed.")

    @validates_schema
    def inputs_and_outputs(self, data, **kwargs):
        ipts: typing.List[raw_nodes.Tensor] = data.get("inputs")
        outs: typing.List[raw_nodes.Tensor] = data.get("outputs")
        if any(
            [
                not isinstance(ipts, list),
                not isinstance(outs, list),
                not all(isinstance(v, raw_nodes.Tensor) for v in ipts),
                not all(isinstance(v, raw_nodes.Tensor) for v in outs),
            ]
        ):
            raise ValidationError("Could not check for duplicate tensor names due to another validation error.")

        # no duplicate tensor names
        names = [t.name for t in ipts + outs]  # type: ignore
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate tensor names are not allowed.")

    test_inputs = fields.List(
        fields.Union([fields.URI(), fields.Path()]),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="List of URIs or local relative paths to test inputs as described in inputs for "
        "**a single test case**. "
        "This means if your workflow has more than one input, you should provide one URI for each input."
        "Each test input should be a file with a ndarray in "
        "[numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format)."
        "The extension must be '.npy'.",
    )
    test_outputs = fields.List(
        fields.Union([fields.URI(), fields.Path()]),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="Analog to test_inputs.",
    )
    steps = fields.List(
        fields.Nested(Step()),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="Workflow steps to be executed consecutively.",
    )
