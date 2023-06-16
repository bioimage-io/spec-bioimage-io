from types import ModuleType
from typing import ClassVar

from marshmallow import EXCLUDE, ValidationError, validates, validates_schema

from bioimageio.spec.shared import (
    BIOIMAGEIO_SITE_CONFIG,
    BIOIMAGEIO_SITE_CONFIG_ERROR,
    LICENSES,
    field_validators,
    fields,
)
from bioimageio.spec.shared.common import get_args, get_patched_format_version
from bioimageio.spec.shared.schema import SharedBioImageIOSchema, WithUnknown
from bioimageio.spec.shared.utils import is_valid_orcid_id
from . import raw_nodes
from .raw_nodes import FormatVersion


class RDF(_BioImageIOSchema):
    class Meta:
        unknown = EXCLUDE

    bioimageio_description = f"""# bioimage.io Resource Description File Specification {get_args(FormatVersion)[-1]}
This specification defines the fields used in a general bioimage.io-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks.
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be
specified.
"""

    config_bioimageio_description = ()
    config = fields.YamlDict(bioimageio_descriptio=config_bioimageio_description)

    covers = fields.List(
        fields.Union([fields.URL(), fields.Path()]),
        bioimageio_description="A list of cover images provided by either a relative path to the model folder, or a "
        "hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height "
        "of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.",  # todo: field_validators image format
    )

    download_url = fields.Union(
        [fields.URL(), fields.Path()], bioimageio_description="optional url to download the resource from"
    )

    format_version = fields.String(
        required=True,
        bioimageio_description_order=0,
        bioimageio_description=(
            "Version of the bioimage.io Resource Description File Specification used."
            f"The current general format version described here is {get_args(FormatVersion)[-1]}. "
            "Note: The general RDF format is not to be confused with specialized RDF format like the Model RDF format."
        ),
    )

    @validates_schema
    def format_version_matches_type(self, data, **kwargs):
        format_version = data.get("format_version")
        type_ = data.get("type")
        try:
            patched_format_version = get_patched_format_version(type_, format_version)
            if format_version.split(".") > patched_format_version.split("."):
                raise ValueError(
                    f"Unknown format_version {format_version} (latest patch: {patched_format_version}; latest format version: )"
                )
        except Exception as e:
            raise ValidationError(f"Invalid format_version {format_version} for RDF type {type_}. (error: {e})")

    @validates("license")
    def warn_about_deprecated_spdx_license(self, value: str):
        license_info = LICENSES.get(value)
        if license_info is None:
            self.warn("license", f"{value} is not a recognized SPDX license identifier. See https://spdx.org/licenses/")
        else:
            if license_info.get("isDeprecatedLicenseId", False):
                self.warn("license", f"{value} ({license_info['name']}) is deprecated.")

            if not license_info.get("isFsfLibre", False):
                self.warn("license", f"{value} ({license_info['name']}) is not FSF Free/libre.")

    name = fields.Name(required=True, bioimageio_description="name of the resource, a human-friendly name")

    @validates
    def warn_about_long_name(self, value: str):
        if isinstance(value, str):
            if len(value) > 64:
                self.warn(
                    "name", f"Length of name ({len(value)}) exceeds the recommended maximum length of 64 characters."
                )
        else:
            self.warn("name", f"Could not check length of name {value}.")

    rdf_source = fields.Union(
        [fields.URL(), fields.DOI()], bioimageio_description="url or doi to the source of the resource definition"
    )
    source = fields.Union(
        [fields.URI(), fields.Path()],
        bioimageio_description="url or local relative path to the source of the resource",
    )

    # todo: restrict valid RDF types?
    @validates("type")
    def validate_type(self, value):
        schema_type = self.__class__.__name__.lower()
        if value != schema_type:
            self.warn("type", f"Unrecognized type '{value}'. Validating as {schema_type}.")

    version = fields.Version(
        bioimageio_description="The version number of the model. The version number format must be a string in "
        "`MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), "
        "e.g. the initial version number should be `0.1.0`."
    )
