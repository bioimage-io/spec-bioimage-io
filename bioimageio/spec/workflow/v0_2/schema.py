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


class Arg(_BioImageIOSchema):
    name = fields.String(
        required=True,
        bioimageio_description="Argument/tensor name. No duplicates are allowed.",
    )
    type = fields.String(
        required=True,
        validate=field_validators.OneOf(get_args(raw_nodes.ArgType)),
        bioimageio_description=f"Argument type. One of: {get_args(raw_nodes.ArgType)}",
    )
    default = fields.Raw(
        required=False,
        bioimageio_description="Default value compatible with type given by `type` field.",
        allow_none=True,
    )

    @validates_schema
    def default_has_compatible_type(self, data, **kwargs):
        if data.get("default") is None:
            return

        arg_type_name = data.get("type")
        if arg_type_name == "any":
            return

        default_type = type(data["default"])
        type_name = raw_nodes.TYPE_NAME_MAP[default_type]
        if type_name != arg_type_name:
            raise ValidationError(
                f"Default value of type {default_type} (type name: {type_name}) does not match type: {arg_type_name}"
            )

    description = fields.String(bioimageio_description="Description of argument/tensor.")


class WorkflowKwarg(_BioImageIOSchema):
    name = fields.String(
        required=True,
        bioimageio_description="Key word argument name. No duplicates are allowed.",
    )
    type = fields.String(
        required=True,
        validate=field_validators.OneOf(get_args(raw_nodes.ArgType)),
        bioimageio_description=f"Argument type. One of: {get_args(raw_nodes.ArgType)}",
    )
    default = fields.Raw(
        required=True,
        bioimageio_description="Default value compatible with type given by `type` field.",
        allow_none=True,
    )

    @validates_schema
    def default_has_compatible_type(self, data, **kwargs):
        if data.get("default") is None:
            return

        arg_type_name = data.get("type")
        if arg_type_name == "any":
            return

        default_type = type(data["default"])
        type_name = raw_nodes.TYPE_NAME_MAP[default_type]
        if type_name != arg_type_name:
            raise ValidationError(
                f"Default value of type {default_type} (type name: {type_name}) does not match type: {arg_type_name}"
            )

    description = fields.String(required=False, bioimageio_description="Description of key word argument.")


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
    kwargs = fields.Kwargs(
        bioimageio_description="Key word arguments for op. \n\nWorkflow kwargs can be refered to as ${{ kwargs.\<workflow kwarg name\> }}. \n\nOutputs of previous steps can be referenced as ${{ \<step id\>.outputs.\<output name\> }} (the previous step is required to specify `id` and `outputs`). \n\nThe workflow's `rdf_source` can be referenced as ${{ self.rdf_source }}. This will expand to the URL or file path of the workflow RDF."
    )


class Workflow(_BioImageIOSchema, RDF):
    bioimageio_description = f"""# BioImage.IO Workflow Resource Description File {get_args(raw_nodes.FormatVersion)[-1]}
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing workflows.
These fields are typically stored in a YAML file which we call Workflow Resource Description File or `workflow RDF`.

The workflow RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
"""
    inputs = fields.List(
        fields.Nested(Arg()),
        required=True,
        bioimageio_description="Describes the inputs expected by this workflow.",
    )

    @validates("inputs")
    def no_duplicate_input_names(self, value: typing.List[raw_nodes.Arg]):
        if not isinstance(value, list) or not all(isinstance(v, raw_nodes.Arg) for v in value):
            raise ValidationError("Could not check for duplicate input names due to another validation error.")

        names = [t.name for t in value]
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate input names are not allowed.")

    outputs = fields.List(
        fields.Nested(Arg()),
        validate=field_validators.Length(min=1),
        bioimageio_description="Describes the outputs from this workflow.",
    )

    @validates("outputs")
    def no_duplicate_output_names(self, value: typing.List[raw_nodes.Arg]):
        if not isinstance(value, list) or not all(isinstance(v, raw_nodes.Arg) for v in value):
            raise ValidationError("Could not check for duplicate output names due to another validation error.")

        names = [t["name"] if isinstance(t, dict) else t.name for t in value]
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate output names are not allowed.")

    @validates_schema
    def inputs_and_outputs(self, data, **kwargs):
        ipts: typing.List[raw_nodes.Arg] = data.get("inputs")
        outs: typing.List[raw_nodes.Arg] = data.get("outputs")
        if any(
            [
                not isinstance(ipts, list),
                not isinstance(outs, list),
                not all(isinstance(v, raw_nodes.Arg) for v in ipts),
                not all(isinstance(v, raw_nodes.Arg) for v in outs),
            ]
        ):
            raise ValidationError("Could not check for duplicate names due to another validation error.")

        # no duplicate names
        names = [t.name for t in ipts + outs]  # type: ignore
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate names are not allowed.")

    kwargs = fields.List(
        fields.Nested(WorkflowKwarg()),
        required=False,
        bioimageio_description="Key word arguments for this workflow.",
    )

    @validates("kwargs")
    def unique_kwarg_names(self, kwargs):
        if not isinstance(kwargs, list) or not all(isinstance(kw, raw_nodes.WorkflowKwarg) for kw in kwargs):
            raise ValidationError("Invalid 'kwargs'.")

        kwarg_names = set()
        for kw in kwargs:
            if kw.name in kwarg_names:
                raise ValidationError(f"Duplicate kwarg name '{kw.name}'.")
            kwarg_names.add(kw.name)

    steps = fields.List(
        fields.Nested(Step()),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="Workflow steps to be executed consecutively.",
    )

    @staticmethod
    def get_kwarg_reference_names(data) -> typing.Set[str]:
        refs: typing.Set[str] = set()
        kwargs = data.get("kwargs")
        if not isinstance(kwargs, list):
            return refs

        for kw in kwargs:
            if isinstance(kw, raw_nodes.WorkflowKwarg):
                refs.add(f"${{{{ kwargs.{kw.name} }}}}")

        return refs

    @staticmethod
    def get_self_reference_names() -> typing.Set[str]:
        return {"${{ self.rdf_source }}"}

    @validates_schema
    def step_input_references_exist(self, data, **kwargs):
        inputs = data.get("inputs")
        if not isinstance(inputs, list) or not all(isinstance(ipt, raw_nodes.Arg) for ipt in inputs):
            raise ValidationError("Missing/invalid 'inputs'")

        steps = data.get("steps")
        if not steps or not isinstance(steps, list) or not all(isinstance(s, raw_nodes.Step) for s in steps):
            raise ValidationError("Missing/invalid 'steps'")

        references = {f"${{{{ inputs.{ipt.name} }}}}" for ipt in inputs}
        references.update(self.get_kwarg_reference_names(data))
        references.update(self.get_self_reference_names())

        for step in steps:
            if step.inputs:
                for si in step.inputs:
                    if si not in references:
                        raise ValidationError(f"Invalid step input reference '{si}'")

            if step.outputs:
                references.update({f"{step.id}.outputs.{out}" for out in step.outputs})

    test_steps = fields.List(
        fields.Nested(Step()),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="Test steps to be executed consecutively.",
    )

    @validates_schema
    def test_step_input_references_exist(self, data, **kwargs):
        steps = data.get("test_steps")
        if not steps or not isinstance(steps, list) or not all(isinstance(s, raw_nodes.Step) for s in steps):
            raise ValidationError("Missing/invalid 'test_steps'")

        references = self.get_kwarg_reference_names(data)
        references.update(self.get_self_reference_names())
        for step in steps:
            if step.inputs:
                for si in step.inputs:
                    if si not in references:
                        raise ValidationError(f"Invalid test step input reference '{si}'")

            if step.outputs:
                references.update({f"{step.id}.outputs.{out}" for out in step.outputs})

    @validates_schema
    def test_kwarg_references_are_valid(self, data, **kwargs):
        for step_type in ["steps", "test_steps"]:
            steps = data.get(step_type)
            if not steps or not isinstance(steps, list) or not isinstance(steps[0], raw_nodes.Step):
                raise ValidationError(f"Missing/invalid '{step_type}'")

            references = self.get_kwarg_reference_names(data)
            references.update(self.get_self_reference_names())
            for step in steps:
                if step.kwargs:
                    for k, v in step.kwargs.items():
                        if isinstance(v, str) and v.startswith("${{") and v.endswith("}}") and v not in references:
                            raise ValidationError(
                                f"Invalid {step_type[:-1].replace('_', ' ')} kwarg ({k}) referencing '{v}'"
                            )

                if step.outputs:
                    references.update({f"${{{{ {step.id}.outputs.{out} }}}}" for out in step.outputs})
