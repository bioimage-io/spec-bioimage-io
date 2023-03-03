import typing
from types import ModuleType
from typing import ClassVar

from marshmallow import ValidationError, validates, validates_schema
from marshmallow.exceptions import SCHEMA

from bioimageio.spec.rdf.v0_2.schema import RDF
from bioimageio.spec.shared import field_validators, fields
from bioimageio.spec.shared.schema import SharedBioImageIOSchema
from . import raw_nodes

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore


class _BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes: ClassVar[ModuleType] = raw_nodes


class Axis(_BioImageIOSchema):
    # name = fields.String(
    #     required=True,
    #     bioimageio_description="A unique axis name (max 32 characters).",
    #     validate=field_validators.Length(min=1, max=32),
    # )
    name = fields.Union(
        [
            fields.String(
                validate=(field_validators.Length(min=1, max=32), field_validators.ContainsNoneOf([","])),
                bioimageio_description="Axis name. Indexed for channel axis, e.g. RGB -> RGB[0],RGB[1],RGB[2]",
            ),
            fields.List(
                fields.String(validate=field_validators.Length(min=1, max=32)),
                bioimageio_description="For channel axis only: Name per channel, e.g. [red, green, blue]",
            ),
        ],
        bioimageio_maybe_required=True,
        bioimageio_description="A unique axis name (max 32 characters)",
    )
    type = fields.String(
        required=True,
        validate=field_validators.OneOf(get_args(raw_nodes.AxisType)),
        bioimageio_description=f"One of: {get_args(raw_nodes.AxisType)}",
    )
    description = fields.String(
        validate=field_validators.Length(min=1, max=128),
        bioimageio_description="Description of axis (max 128 characters).",
        bioimageio_maybe_required=True,
    )
    unit = fields.Union(
        [
            fields.String(validate=(field_validators.Length(min=1, max=32), field_validators.ContainsNoneOf([","]))),
            fields.List(
                fields.String(validate=field_validators.Length(min=1, max=32)),
                bioimageio_description="For channel axis only: unit of data values (max 32 characters; per channel if list).",
            ),
        ],
        bioimageio_description="Physical unit of this axis (max 32 characters).",
        bioimageio_maybe_required=True,
    )
    # unit = fields.String(bioimageio_description="Physical unit of this axis.", bioimageio_maybe_required=True)
    # Recommendations:\n\n for type: 'space' one of:\n\n\t{get_args(raw_nodes.SpaceUnit)}\n\n for type: 'time' one of:\n\n\t{get_args(raw_nodes.TimeUnit)}")
    step = fields.Float(
        bioimageio_description="One 'pixel' along this axis corresponds to 'step' 'unit'. (Invalid for channel axis.)"
    )
    scaling_factor = fields.Union(
        [
            fields.Float(
                validate=field_validators.Range(min=0, min_inclusive=False),
                bioimageio_description="Scaling factor for all channels.",
            ),
            fields.List(
                fields.Float(validate=field_validators.Range(min=0, min_inclusive=False)),
                bioimageio_description="Scaling factor per channel.",
            ),
        ],
        bioimageio_description="For channel axis only: Scaling factor (per channel). Values are given in 'scaling_factor' 'unit'.",
    )

    @validates_schema
    def step_has_unit(self, data, **kwargs):
        if "step" in data and not "unit" in data:
            raise ValidationError("Missing 'unit' for specified 'step'.", "unit")

    @validates_schema
    def validate_type_specifics(self, data, **kwargs):
        type_ = data.get("type")
        unit = data.get("unit")
        for invalid in dict(
            batch=["scaling_factor", "step", "unit", "description", "name"],
            channel=["step"],
            index=["unit", "step", "scaling_factor"],
            space=["scaling_factor"],
            time=["scaling_factor"],
        ).get(type_, []):
            if invalid in data:
                raise ValidationError(f"'{invalid}' invalid for {type_} axis")

        if type_ != "channel" and isinstance(data.get("name"), list):
            raise ValidationError(
                f"A list of names is only valid for axis type channel, not axis type {data.get('type')}."
            )

        if type_ == "space":
            if data.get("name") not in "xyz":
                raise ValidationError("For a space axis only the names 'x', 'y', or 'z' are allowed.")

            recommended_units = get_args(raw_nodes.SpaceUnit)
            if unit not in recommended_units:
                self.warn("unit", f"unknown unit '{unit}' for space axis. Recommend units are: {recommended_units}.")

        if type_ == "time":
            recommended_units = get_args(raw_nodes.TimeUnit)
            if unit not in recommended_units:
                self.warn("unit", f"unknown unit '{unit}' for time axis. Recommend units are: {recommended_units}.")


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
    axes = fields.Union(
        [
            fields.List(fields.Nested(Axis())),
            fields.String(
                bioimageio_description="Arbitrary or unknown combination of valid axis types.",
                validate=field_validators.Equal(get_args(raw_nodes.UnknownAxes)[0]),
            ),
        ],
        required=False,
        bioimageio_maybe_required=True,
        bioimageio_description="Axis specifications (only required for type 'tensor').",
    )
    description = fields.String(
        bioimageio_description="Description (max 128 characters).", validate=field_validators.Length(min=1, max=128)
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
        type_name = raw_nodes.TYPE_NAMES[default_type]
        if type_name != input_type_name:
            raise ValidationError(
                f"Default value of type {default_type} (type name: {type_name}) does not match type: {input_type_name}"
            )


class Output(Parameter):
    pass


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
    def verify_param_list(params: typing.Any) -> typing.List[raw_nodes.Parameter]:
        if not isinstance(params, list) or not all(isinstance(v, raw_nodes.Parameter) for v in params):
            raise ValidationError("Could not check for duplicate parameter names due to another validation error.")

        return params

    @staticmethod
    def check_for_duplicate_param_names(
        params: typing.List[typing.Union[raw_nodes.Parameter]], param_name: str, field_name=SCHEMA
    ):
        names = set()
        for t in params:
            if not isinstance(t, raw_nodes.Parameter):
                raise ValidationError(
                    f"Could not check for duplicate {param_name} name due to other validation errors."
                )

            if t.name in names:
                raise ValidationError(f"Duplicate {param_name} name '{t.name}' not allowed.", field_name)

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
            self.check_for_duplicate_param_names(self.verify_param_list(ipts + opts), "input/option", "inputs/options")

    outputs = fields.List(
        fields.Nested(Output()),
        validate=field_validators.Length(min=1),
        bioimageio_description="Describes the outputs of this workflow.",
    )

    @validates("outputs")
    def no_duplicate_output_names(self, outs: typing.List[raw_nodes.Output]):
        self.check_for_duplicate_param_names(self.verify_param_list(outs), "outputs")

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
