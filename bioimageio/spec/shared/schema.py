import warnings
from types import ModuleType
from typing import ClassVar, List

from marshmallow import INCLUDE, Schema, ValidationError, post_dump, post_load, validates, validates_schema

from bioimageio.spec.shared import fields
from . import raw_nodes
from .common import ValidationWarning


class SharedBioImageIOSchema(Schema):
    raw_nodes: ClassVar[ModuleType] = raw_nodes  # to be overwritten in subclass by version specific raw_nodes module
    short_bioimageio_description: ClassVar[str] = ""
    bioimageio_description: ClassVar[str] = ""

    @post_load
    def make_object(self, data, **kwargs):
        if data is None:
            return None

        this_type = getattr(self.raw_nodes, self.__class__.__name__, None)
        if this_type is None:
            # attempt import from shared raw nodes
            this_type = getattr(raw_nodes, self.__class__.__name__, None)
            if this_type is None:
                raise NotImplementedError(
                    f"neither {self.raw_nodes} nor {raw_nodes} has attribute {self.__class__.__name__}."
                )

        try:
            return this_type(**data)
        except TypeError as e:
            e.args += (f"when initializing {this_type} from {self}",)
            raise e

    def warn(self, field: str, msg: str):
        """warn about a field with a ValidationWarning"""
        # simple_field_name = field.split("[")[0]  # field may include [idx]
        # field_instance = self.fields[simple_field_name]  # todo: account for <field>:<nested field>
        assert ": " not in field
        # todo: add spec trail to field
        # e.g. something similar to field = ":".join(self.context.get("field_path", []) + [field])
        # or: ":".join(field_instance.spec_trail)
        msg = f"{field}: {msg}"
        warnings.warn(msg, category=ValidationWarning)


class SharedProcessingSchema(Schema):
    """Used to generate Pre- and Postprocessing documentation.

    Define Pre-/Postprocessing schemas in the Preprocessing/Postprocessing schema that inherite from this class
    and they will be rendered in the documentation."""

    bioimageio_description: ClassVar[str]


class WithUnknown(SharedBioImageIOSchema):
    """allows to keep unknown fields on load and dump them the 'unknown' attribute of the data to serialize"""

    field_name_unknown_dict = "unknown"

    class Meta:
        unknown = INCLUDE

    @post_load
    def make_object(self, data, **kwargs):
        obj = super().make_object(data, **kwargs)
        assert hasattr(
            obj, self.field_name_unknown_dict
        ), f"expected raw node to have attribute {self.field_name_unknown_dict}"
        return obj

    @post_dump(pass_original=True)
    def keep_unknowns(self, output, orig, **kwargs):
        if orig and hasattr(orig, self.field_name_unknown_dict):
            out_w_unknown = fields.YamlDict()._serialize(
                getattr(orig, self.field_name_unknown_dict), self.field_name_unknown_dict, self
            )
            out_w_unknown.update(output)
            return out_w_unknown
        else:
            return output


class Dependencies(SharedBioImageIOSchema):
    manager = fields.String(bioimageio_description="Dependency manager For example: 'conda', 'maven', or 'pip'")
    file = fields.Union(
        [fields.URI(), fields.Path()],
        bioimageio_description="Dependency file. For example: 'environment.yaml', 'pom.xml', or 'requirements.txt'",
    )


class ParametrizedInputShape(SharedBioImageIOSchema):
    min = fields.List(
        fields.Integer(), required=True, bioimageio_description="The minimum input shape with same length as `axes`"
    )
    step = fields.List(
        fields.Integer(), required=True, bioimageio_description="The minimum shape change with same length as `axes`"
    )

    @validates_schema
    def matching_lengths(self, data, **kwargs):
        min_ = data["min"]
        step = data["step"]
        if min_ is None or step is None:
            return

        if len(min_) != len(step):
            raise ValidationError(f"'min' and 'step' have to have the same length! (min: {min_}, step: {step})")


class ImplicitOutputShape(SharedBioImageIOSchema):
    reference_tensor = fields.String(required=True, bioimageio_description="Name of the reference tensor.")
    scale = fields.List(
        fields.Float(allow_none=True),
        required=True,
        bioimageio_description="'output_pix/input_pix' for each dimension.",
    )
    offset = fields.List(
        fields.Float(), required=True, bioimageio_description="Position of origin wrt to input. Multiple of 0.5."
    )

    @validates_schema
    def matching_lengths(self, data, **kwargs):
        scale = data["scale"]
        offset = data["offset"]
        if len(scale) != len(offset):
            raise ValidationError(f"scale {scale} has to have same length as offset {offset}!")
        # if we have an expanded dimension, make sure that it's offet is not zero
        if any(sc is None for sc in scale):
            for sc, off in zip(scale, offset):
                if sc is None and off == 0:
                    raise ValidationError("Offset must not be 0 for scale null")

    @validates("offset")
    def double_offset_is_int(self, value: List[float]):
        for v in value:
            if 2 * v != int(2 * v):
                raise ValidationError(f"offset {v} in {value} not a multiple of 0.5!")
