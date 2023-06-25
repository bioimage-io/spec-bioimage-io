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
