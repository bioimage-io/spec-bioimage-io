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


class _BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class Attachments(_BioImageIOSchema, WithUnknown):
    files = fields.List(
        fields.Union([fields.URI(), fields.Path()]),
        bioimageio_description="File attachments; included when packaging the resource.",
    )


class _Person(_BioImageIOSchema):
    name = fields.Name(bioimageio_description="Full name.")
    affiliation = fields.String(bioimageio_description="Affiliation.")
    email = fields.Email()
    github_user = fields.String(bioimageio_description="GitHub user name.")  # todo: add validation?
    orcid = fields.String(
        validate=[
            field_validators.Length(19),
            lambda oid: all(oid[idx] == "-" for idx in [4, 9, 14]),
            lambda oid: is_valid_orcid_id(oid.replace("-", "")),
        ],
        bioimageio_description="[orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id "
        "in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid]("
        "https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier"
        ") as per ISO 7064 11,2.)",
    )


class Author(_Person):
    name = fields.Name(require=True, bioimageio_description="Full name.")


class Maintainer(_Person):
    github_user = fields.String(require=True, bioimageio_description="GitHub user name.")


class Badge(_BioImageIOSchema):
    bioimageio_description = "Custom badge."
    label = fields.String(required=True, bioimageio_description="e.g. 'Open in Colab'")
    icon = fields.String(bioimageio_description="e.g. 'https://colab.research.google.com/assets/colab-badge.svg'")
    url = fields.Union(
        [fields.URL(), fields.Path()],
        bioimageio_description="e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'",
    )


class CiteEntry(_BioImageIOSchema):
    text = fields.String(required=True, bioimageio_description="free text description")
    doi = fields.DOI(
        bioimageio_maybe_required=True, bioimageio_description="digital object identifier, see https://www.doi.org/"
    )
    url = fields.String(bioimageio_maybe_required=True)  # todo: change to fields.URL

    @validates_schema
    def doi_or_url(self, data, **kwargs):
        if data.get("doi") is None and data.get("url") is None:
            raise ValidationError("doi or url needs to be specified in a citation")


class RDF(_BioImageIOSchema):
    class Meta:
        unknown = EXCLUDE

    bioimageio_description = f"""# BioImage.IO Resource Description File Specification {get_args(FormatVersion)[-1]}
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by 
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be 
specified.
"""

    attachments = fields.Nested(Attachments(), bioimageio_description="Additional unknown keys are allowed.")

    authors_bioimageio_description = (
        "A list of authors. The authors are the creators of the specifications and the primary points of contact."
    )
    authors = fields.List(fields.Nested(Author()), bioimageio_description=authors_bioimageio_description)

    badges = fields.List(fields.Nested(Badge()), bioimageio_description="a list of badges")

    cite_bioimageio_description = """A list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used."""
    cite = fields.List(fields.Nested(CiteEntry()), bioimageio_description=cite_bioimageio_description)

    config_bioimageio_description = (
        "A custom configuration field that can contain any keys not present in the RDF spec. "
        "This means you should not store, for example, github repo URL in `config` since we already have the "
        "`git_repo` key defined in the spec.\n"
        "Keys in `config` may be very specific to a tool or consumer software. To avoid conflicted definitions, "
        "it is recommended to wrap configuration into a sub-field named with the specific domain or tool name, "
        """for example:

```yaml
   config:
      bioimage_io:  # here is the domain name
        my_custom_key: 3837283
        another_key:
           nested: value
      imagej:
        macro_dir: /path/to/macro/file
```
"""
        "If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`."
    )
    config = fields.YamlDict(bioimageio_descriptio=config_bioimageio_description)

    covers = fields.List(
        fields.Union([fields.URL(), fields.Path()]),
        bioimageio_description="A list of cover images provided by either a relative path to the model folder, or a "
        "hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height "
        "of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.",  # todo: field_validators image format
    )

    description = fields.String(required=True, bioimageio_description="A string containing a brief description.")

    documentation = fields.Union(
        [
            fields.URL(),
            fields.Path(
                validate=field_validators.Attribute(
                    "suffix",
                    field_validators.Equal(
                        ".md", error="{!r} is invalid; expected markdown file with '.md' extension."
                    ),
                )
            ),
        ],
        bioimageio_description="URL or relative path to markdown file with additional documentation. "
        "For markdown files the recommended documentation file name is `README.md`.",
    )

    download_url = fields.Union(
        [fields.URL(), fields.Path()], bioimageio_description="optional url to download the resource from"
    )

    format_version = fields.String(
        required=True,
        bioimageio_description_order=0,
        bioimageio_description=(
            "Version of the BioImage.IO Resource Description File Specification used."
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

    git_repo_bioimageio_description = "A url to the git repository, e.g. to Github or Gitlab."
    git_repo = fields.URL(bioimageio_description=git_repo_bioimageio_description)

    icon = fields.String(
        bioimageio_description="an icon for the resource"
    )  # todo: limit length? validate=field_validators.Length(max=1)

    id = fields.String(bioimageio_description="Unique id within a collection of resources.")
    license_bioimageio_description = (
        "A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, "
        "`BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send "
        "an Github issue to discuss your intentions with the community."
    )
    license = fields.String(  # todo: make mandatory?
        # validate=field_validators.OneOf(LICENSES),  # enforce license id
        bioimageio_description=license_bioimageio_description
    )

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

    links = fields.List(fields.String(), bioimageio_description="links to other bioimage.io resources")

    maintainers = fields.List(fields.Nested(Maintainer()), bioimageio_description="Maintainers of this resource.")

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

    tags = fields.List(fields.String(), bioimageio_description="A list of tags.")

    @validates("tags")
    def warn_about_tag_categories(self, value):
        if BIOIMAGEIO_SITE_CONFIG is None:
            error = BIOIMAGEIO_SITE_CONFIG_ERROR
        else:
            missing_categories = []
            try:
                categories = {
                    c["type"]: c.get("tag_categories", {}) for c in BIOIMAGEIO_SITE_CONFIG["resource_categories"]
                }.get(self.__class__.__name__.lower(), {})
                for cat, entries in categories.items():
                    if not any(e in value for e in entries):
                        missing_categories.append({cat: entries})
            except Exception as e:
                error = str(e)
            else:
                error = None
                if missing_categories:
                    self.warn("tags", f"Missing tags for categories: {missing_categories}")

        if error is not None:
            self.warn("tags", f"could not check tag categories ({error})")

    type = fields.String(required=True)

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
