import typing

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


class Parameter(_BioImageIOSchema):
    name = fields.String(
        required=True,
        bioimageio_description="Parameter name. No duplicates are allowed.",
    )
    type = fields.String(
        required=True,
        validate=field_validators.OneOf(get_args(raw_nodes.ParameterType)),
        bioimageio_description=f"Parameter type. One of: {get_args(raw_nodes.ParameterType)}",
    )
    axes = fields.Axes(
        required=False,
        bioimageio_maybe_required=True,
        bioimageio_description="[only applicable if type is 'tensor'] one letter out of 'bitczyx' per tensor dimension",
        valid_axes="bitczyx",
    )
    description = fields.String(bioimageio_description="Description of parameter.")

    @validates_schema
    def has_axes_if_tensor(self, data, **kwargs):
        ipt_type = data.get("type")
        axes = data.get("axes")
        if ipt_type == "tensor" and axes is None:
            raise ValidationError("'axes' required for input type 'tensor'.")


class Input(Parameter):
    default = fields.Raw(
        required=False,
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
    id = fields.String(
        required=False,
        bioimageio_maybe_required=True,
        validate=field_validators.Predicate("isidentifier"),
        bioimageio_description="Step id for referencing the steps' kwargs or outputs.",
    )

    @validates_schema
    def has_id_if_outputs(self, data, **kwargs):
        if data.get("outputs") and "id" not in data:
            raise ValidationError("'id' required if 'outputs' are named.")

    op = fields.String(
        required=True,
        validate=field_validators.Predicate("isidentifier"),
        bioimageio_description="Name of operation. Must be implemented in bioimageio.core or bioimageio.contrib.",
    )
    inputs = fields.Union(
        [
            fields.List(fields.Raw()),
            fields.YamlDict(fields.String(validate=field_validators.Predicate("isidentifier")), fields.Raw()),
        ],
        bioimageio_description="Either a list of input parameters (named parameters as dict with one entry after all positional parameters)."
        "\n\nOr a dictionary of named parameters."
        "\n\nIf not set the outputs of the previous step are used as positional input parameters.",
    )
    outputs = fields.List(
        fields.String(
            validate=field_validators.Predicate("isidentifier"),
        ),
        required=False,
        bioimageio_description="Output names for this step.",
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
    def check_for_duplicate_param_names(params: typing.List[typing.Union[raw_nodes.Parameter]]):
        names = set()
        for t in params:
            if t.name in names:
                raise ValidationError(f"Duplicate parameter name '{t.name}' not allowed.")

            names.add(t.name)

    @validates("inputs")
    def no_duplicate_input_names(self, ipts: typing.List[raw_nodes.Input]):
        self.check_for_duplicate_param_names(self.verify_param_list(ipts))

    outputs = fields.List(
        fields.Nested(Output()),
        validate=field_validators.Length(min=1),
        bioimageio_description="Describes the outputs from this workflow.",
    )

    @validates("outputs")
    def no_duplicate_output_names(self, outs: typing.List[raw_nodes.Output]):
        self.check_for_duplicate_param_names(self.verify_param_list(outs))

    @staticmethod
    def get_input_reference_names(data) -> typing.Set[str]:
        refs: typing.Set[str] = set()
        inputs = data.get("inputs")
        if not isinstance(inputs, list):
            return refs

        for ipt in inputs:
            if isinstance(ipt, raw_nodes.Input):
                refs.add(f"${{{{ inputs.{ipt.name} }}}}")

        return refs

    @staticmethod
    def get_self_reference_names() -> typing.Set[str]:
        return {"${{ self.rdf_source }}"}

    test_steps = fields.List(
        fields.Nested(Step()),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="Test steps to be executed consecutively.",
    )

    @validates_schema
    def step_inputs_are_valid(self, data, **kwargs):
        for step_type in ["steps", "test_steps"]:
            steps = data.get(step_type)
            if not steps or not isinstance(steps, list) or not isinstance(steps[0], raw_nodes.Step):
                raise ValidationError(f"Missing/invalid '{step_type}'")

            references = self.get_input_reference_names(data)
            references.update(self.get_self_reference_names())
            for step in steps:
                if isinstance(step.inputs, list):
                    for si in step.inputs:
                        if isinstance(si, str) and si.startswith("${{") and si.endwith("}}") and si not in references:
                            raise ValidationError(f"Invalid reference '{si}'")
                        elif isinstance(si, dict) and len(si) == 1:
                            si_ref = list(si.values())[0]
                            if si_ref not in references:
                                raise ValidationError(f"Invalid reference '{si_ref}'")

                elif isinstance(step.inputs, dict):
                    for key, value in step.inputs.values():
                        if key.startswith("${{") and key.endswith("}}"):
                            raise ValidationError("Invalid input name. (no reference allowed here)")
                        if value.startswith("${{") and value.endswith("}}") and value not in references:
                            raise ValidationError(f"Invalid reference '{value}'")

                if step.outputs:
                    references.update({f"{step.id}.outputs.{out}" for out in step.outputs})

                    for k, v in step.kwargs.items():
                        if isinstance(v, str) and v.startswith("${{") and v.endswith("}}") and v not in references:
                            raise ValidationError(
                                f"Invalid {step_type[:-1].replace('_', ' ')} kwarg ({k}) referencing '{v}'"
                            )

                if step.outputs:
                    references.update({f"${{{{ {step.id}.outputs.{out} }}}}" for out in step.outputs})
