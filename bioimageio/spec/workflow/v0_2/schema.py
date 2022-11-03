import typing
import warnings

from marshmallow import ValidationError, missing, validates, validates_schema

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


class Axis(SharedBioImageIOSchema):
    name = fields.String(
        required=True,
        bioimageio_description="A unique axis name (max 32 characters).",
        validate=field_validators.Length(max=32),
    )
    type = fields.String(
        required=True,
        validate=field_validators.OneOf(get_args(raw_nodes.AxisType)),
        bioimageio_description=f"One of: {get_args(raw_nodes.AxisType)}",
    )
    description = fields.String(
        validate=field_validators.Length(max=128),
        bioimageio_description="Description of axis (max 128 characters).",
    )
    unit = fields.String(bioimageio_description="Physical unit of this axis.", bioimageio_maybe_required=True)
    # Recommendations:\n\n for type: 'space' one of:\n\n\t{get_args(raw_nodes.SpaceUnit)}\n\n for type: 'time' one of:\n\n\t{get_args(raw_nodes.TimeUnit)}")
    step = fields.Integer(
        bioimageio_description="One 'pixel' along this axis corresponds to 'step'+'unit'. If specified 'unit' is mandatory."
    )

    @validates_schema
    def step_has_unit(self, data, **kwargs):
        if "step" in data and not "unit" in data:
            raise ValidationError("Missing 'unit' for specified 'step'.", "unit")


class BatchAxis(Axis):
    class Meta:
        exclude = ("name", "description", "unit", "step")

    type = fields.String(required=True, validate=field_validators.Equal("batch"), bioimageio_description="'batch'")


class ChannelAxis(Axis):
    class Meta:
        exclude = ("step",)

    type = fields.String(required=True, validate=field_validators.Equal("channel"), bioimageio_description="'channel'")
    name = fields.Union(
        [
            fields.List(fields.String(validate=field_validators.Length(max=32))),
            fields.String(validate=field_validators.Length(max=32)),
        ],
        required=True,
        bioimageio_description="A unique axis name (max 32 characters; per channel if list).",
    )
    unit = fields.Union(
        [
            fields.List(fields.String(validate=field_validators.Length(max=32))),
            fields.String(validate=field_validators.Length(max=32)),
        ],
        required=True,
        bioimageio_description="Physical unit of data values (max 32 characters; per channel if list).",
    )


class IndexAxis(Axis):
    class Meta:
        exclude = ("step", "unit")

    type = fields.String(required=True, validate=field_validators.Equal("index"), bioimageio_description="'index'")


class SpaceAxis(Axis):
    name = fields.String(
        validate=field_validators.OneOf(["x", "y", "z"]),
        required=True,
        bioimageio_description="One of: ['x', 'y', 'z'].",
    )
    type = fields.String(required=True, validate=field_validators.Equal("space"), bioimageio_description="'space'")

    @validates("unit")
    def recommend_unit(self, value: str):
        recommended_units = get_args(raw_nodes.SpaceUnit)
        if not value in recommended_units:
            self.warn("unit", f"unknown space unit {value}. Recommend units are: {recommended_units}")


class TimeAxis(Axis):
    type = fields.String(required=True, validate=field_validators.Equal("time"), bioimageio_description="'time'")

    @validates("unit")
    def recommend_unit(self, value: str):
        recommended_units = get_args(raw_nodes.TimeUnit)
        if not value in recommended_units:
            self.warn("unit", f"unknown time unit {value}. Recommend units are: {recommended_units}")


class Parameter(_BioImageIOSchema):
    name = fields.String(
        required=True,
        bioimageio_description="Parameter name. No duplicates are allowed.",
    )
    type = fields.String(
        required=True,
        validate=field_validators.OneOf(get_args(raw_nodes.ParameterType)),
        bioimageio_description=f"One of: {get_args(raw_nodes.ParameterType)}",
    )
    axes = fields.List(
        fields.Union(
            [
                fields.Nested(BatchAxis()),
                fields.Nested(ChannelAxis()),
                fields.Nested(IndexAxis()),
                fields.Nested(SpaceAxis()),
                fields.Nested(TimeAxis()),
            ]
        ),
        required=False,
        bioimageio_maybe_required=True,
        bioimageio_description="Axis specifications (only required for type 'tensor').",
    )
    description = fields.String(
        bioimageio_description="Description (max 128 characters).", validate=field_validators.Length(max=128)
    )

    @validates_schema
    def has_axes_if_tensor(self, data, **kwargs):
        ipt_type = data.get("type")
        axes = data.get("axes")
        if ipt_type == "tensor" and axes is None:
            raise ValidationError("'axes' required for input type 'tensor'.")


class Input(Parameter):
    pass


class Option(Parameter):
    default = fields.Raw(
        required=True,
        bioimageio_description="Default value compatible with type given by `type` field."
        "\n\nThe `null` value is compatible with any specified type.",
        allow_none=True,
    )

    @validates_schema
    def default_has_compatible_type(self, data, **kwargs):
        if data.get("default") is None:
            # no default or always valid default of None
            return

        input_type_name = data.get("type")
        if input_type_name == "any":
            return

        default_type = type(data["default"])
        type_name = raw_nodes.TYPE_NAME_MAP[default_type]
        if type_name != input_type_name:
            raise ValidationError(
                f"Default value of type {default_type} (type name: {type_name}) does not match type: {input_type_name}"
            )


class Output(Parameter):
    pass


class Step(_BioImageIOSchema):
    op = fields.String(
        required=True,
        validate=field_validators.Predicate("isidentifier"),
        bioimageio_description="Name of operation. Must be implemented in bioimageio.core or bioimageio.contrib.",
    )
    id = fields.String(
        required=False,
        bioimageio_maybe_required=True,
        validate=[field_validators.Predicate("isidentifier"), field_validators.NoneOf(["self"])],
        bioimageio_description="Step id for referencing the steps' outputs (must not be 'self').",
    )

    @validates_schema
    def has_id_if_outputs(self, data, **kwargs):
        if data.get("outputs") and "id" not in data:
            raise ValidationError("'id' required if 'outputs' are named.")

    inputs = fields.List(
        fields.Raw(),
        bioimageio_description="A list of input parameters. Named outputs of previous steps may be referenced as '${{ \\<step id\\>.outputs.\\<output name\\> }}'"
        "\n\nIf not set, the outputs of the previous step are used as inputs.",
    )
    outputs = fields.List(
        fields.String(
            validate=field_validators.Predicate("isidentifier"),
        ),
        required=False,
        bioimageio_description="Output names for this step for later referencing.",
    )


class Workflow(_BioImageIOSchema, RDF):
    bioimageio_description = f"""# BioImage.IO Workflow Resource Description File {get_args(raw_nodes.FormatVersion)[-1]}
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing workflows.
These fields are typically stored in a YAML file which we call Workflow Resource Description File or `workflow RDF`.

The workflow RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.

"""
    inputs = fields.List(
        fields.Nested(Input()),
        required=True,
        bioimageio_description="Describes the inputs expected by this workflow.",
    )

    @staticmethod
    def verify_param_list(params: typing.Any) -> typing.List[typing.Union[raw_nodes.Parameter]]:
        if not isinstance(params, list) or not all(isinstance(v, raw_nodes.Parameter) for v in params):
            raise ValidationError("Could not check for duplicate parameter names due to another validation error.")

        return params

    @staticmethod
    def check_for_duplicate_param_names(params: typing.List[typing.Union[raw_nodes.Parameter]], param_name: str):
        names = set()
        for t in params:
            if not isinstance(t, raw_nodes.Parameter):
                raise ValidationError(
                    f"Could not check for duplicate {param_name} name due to other validation errors."
                )

            if t.name in names:
                raise ValidationError(f"Duplicate {param_name} name '{t.name}' not allowed.")

            names.add(t.name)

    options = fields.List(
        fields.Nested(Option()),
        required=True,
        bioimageio_description="Describes the options that may be given to this workflow.",
    )

    @validates_schema
    def no_duplicate_input_and_option_names(self, data, **kwargs):
        if not isinstance(data, dict):
            return
        ipts = data.get("inputs", [])
        opts = data.get("options", [])
        if isinstance(ipts, list) and isinstance(opts, list):
            self.check_for_duplicate_param_names(self.verify_param_list(ipts + opts), "input/option")

    outputs = fields.List(
        fields.Nested(Output()),
        validate=field_validators.Length(min=1),
        bioimageio_description="Describes the outputs of this workflow.",
    )

    @validates("outputs")
    def no_duplicate_output_names(self, outs: typing.List[raw_nodes.Output]):
        self.check_for_duplicate_param_names(self.verify_param_list(outs), "output")

    @staticmethod
    def get_initial_reference_names(data) -> typing.Set[str]:
        refs = {"${{ self.rdf_source }}"}
        inputs = data.get("inputs")
        if not isinstance(inputs, list):
            return refs

        for ipt in inputs:
            if isinstance(ipt, raw_nodes.Input):
                refs.add(f"${{{{ self.inputs.{ipt.name} }}}}")

        options = data.get("options")
        if not isinstance(options, list):
            return refs

        for opt in options:
            if isinstance(opt, raw_nodes.Option):
                refs.add(f"${{{{ self.options.{opt.name} }}}}")

        return refs

    test_steps = fields.List(
        fields.Nested(Step()),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="Test steps to be executed consecutively.",
    )

    @validates_schema
    def step_inputs_and_options_are_valid(self, data, **kwargs):
        for step_type in ["steps", "test_steps"]:
            steps = data.get(step_type)
            if not steps or not isinstance(steps, list) or not isinstance(steps[0], raw_nodes.Step):
                raise ValidationError(f"Missing/invalid '{step_type}'")

            references = self.get_initial_reference_names(data)
            for step in steps:
                if isinstance(step.inputs, list):
                    for si in step.inputs:
                        if isinstance(si, str) and si.startswith("${{") and si.endwith("}}") and si not in references:
                            raise ValidationError(f"Invalid reference '{si}'")

                if step.options:
                    for k, v in step.options.items():
                        if isinstance(v, str) and v.startswith("${{") and v.endswith("}}") and v not in references:
                            raise ValidationError(
                                f"Invalid {step_type[:-1].replace('_', ' ')} option ({k}) referencing '{v}'"
                            )

                if step.outputs:
                    references.update({f"${{{{ {step.id}.outputs.{out} }}}}" for out in step.outputs})
