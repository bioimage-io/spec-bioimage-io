from types import ModuleType
from typing import ClassVar

from marshmallow import Schema, ValidationError, post_load, validates, validates_schema

from bioimageio.spec.shared import fields
from . import raw_nodes


class SharedBioImageIOSchema(Schema):
    raw_nodes: ClassVar[ModuleType] = raw_nodes  # to be overwritten in subclass by version specific raw_nodes module
    bioimageio_description: ClassVar[str] = ""

    @post_load
    def make_object(self, data, **kwargs):
        if not data:
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


class SharedProcessingSchema(Schema):
    """Used to generate Pre- and Postprocessing documentation.

    Define Pre-/Postprocessing schemas in the Preprocessing/Postprocessing schema that inherite from this class
    and they will be rendered in the documentation."""

    bioimageio_description: ClassVar[str]


class Dependencies(SharedBioImageIOSchema):
    manager = fields.String(bioimageio_description="Dependency manager For example: 'conda', 'maven', or 'pip'")
    file = fields.Union(
        [fields.URI(), fields.RelativeLocalPath()],
        bioimageio_description="Dependency file. For example: 'environment.yaml', 'pom.xml', or 'requirements.txt'",
    )


class ParametrizedInputShape(SharedBioImageIOSchema):
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
    reference_tensor = fields.String(required=True, bioimageio_description="Name of the reference tensor.")
    scale = fields.List(
        fields.Float, required=True, bioimageio_description="'output_pix/input_pix' for each dimension."
    )
    offset = fields.List(
        fields.Float, required=True, bioimageio_description="Position of origin wrt to input. Multiple of 0.5."
    )

    @validates_schema
    def matching_lengths(self, data, **kwargs):
        scale = data["scale"]
        offset = data["offset"]
        if len(scale) != len(offset):
            raise ValidationError(f"scale {scale} has to have same length as offset {offset}!")

    @validates("offset")
    def double_offset_is_int(self, value):
        for v in value:
            if 2 * v != int(2 * v):
                raise ValidationError(f"offset {v} in {value} not a multiple of 0.5!")
