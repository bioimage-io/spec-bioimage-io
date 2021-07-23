from types import ModuleType
from typing import ClassVar

from marshmallow import Schema, ValidationError, post_load, validates_schema

from bioimageio.spec.shared import fields
from . import raw_nodes


class SharedBioImageIOSchema(Schema):
    raw_nodes: ClassVar[ModuleType] = raw_nodes  # to be overwritten in subclass by version specific raw_nodes module
    bioimageio_description: str = ""

    @post_load
    def make_object(self, data, **kwargs):
        if not data:
            return None

        this_type = getattr(self.raw_nodes, self.__class__.__name__, None)
        if this_type is None:
            # attempt import from shared raw nodes
            this_type = getattr(raw_nodes, self.__class__.__name__, None)
            if this_type is None:
                raise AttributeError(
                    f"neither {self.raw_nodes} nor {raw_nodes} has attribute {self.__class__.__name__}."
                )

        try:
            return this_type(**data)
        except TypeError as e:
            e.args += (f"when initializing {this_type} from {self}",)
            raise e


class ImplicitInputShape(SharedBioImageIOSchema):
    min = fields.List(
        fields.Integer, required=True, bioimageio_description="The minimum input shape with same length as `axes`"
    )
    step = fields.List(
        fields.Integer, required=True, bioimageio_description="The minimum shape change with same length as `axes`"
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
    reference_input = fields.String(required=True, bioimageio_description="Name of the reference input tensor.")
    scale = fields.List(
        fields.Float, required=True, bioimageio_description="'output_pix/input_pix' for each dimension."
    )
    offset = fields.List(fields.Integer, required=True, bioimageio_description="Position of origin wrt to input.")

    @validates_schema
    def matching_lengths(self, data, **kwargs):
        scale = data["scale"]
        offset = data["offset"]
        if len(scale) != len(offset):
            raise ValidationError(f"scale {scale} has to have same length as offset {offset}!")
