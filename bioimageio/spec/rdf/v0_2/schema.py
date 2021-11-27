import warnings

from marshmallow import EXCLUDE, ValidationError, validates, validates_schema

from bioimageio.spec.shared import LICENSES, field_validators, fields
from bioimageio.spec.shared.common import get_args, get_patched_format_version
from bioimageio.spec.shared.schema import SharedBioImageIOSchema
from bioimageio.spec.shared.utils import is_valid_orcid_id
from . import raw_nodes
from .raw_nodes import FormatVersion


class BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class Author(BioImageIOSchema):
    name = fields.String(required=True, bioimageio_description="Full name.")
    affiliation = fields.String(bioimageio_description="Affiliation.")
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


class Badge(BioImageIOSchema):
    bioimageio_description = "Custom badge"
    label = fields.String(required=True, bioimageio_description="e.g. 'Open in Colab'")
    icon = fields.String(bioimageio_description="e.g. 'https://colab.research.google.com/assets/colab-badge.svg'")
    url = fields.Union(
        [fields.URI(), fields.RelativeLocalPath()],  # todo: make url only?
        bioimageio_description="e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'",
    )


class CiteEntry(BioImageIOSchema):
    text = fields.String(required=True)
    doi = fields.String(bioimageio_maybe_required=True)
    url = fields.String(bioimageio_maybe_required=True)

    @validates_schema
    def doi_or_url(self, data, **kwargs):
        if data.get("doi") is None and data.get("url") is None:
            raise ValidationError("doi or url needs to be specified in a citation")


class RunMode(BioImageIOSchema):
    name = fields.String(
        required=True, bioimageio_description="The name of the `run_mode`"
    )  # todo: limit valid run mode names
    kwargs = fields.Kwargs()


class RDF(BioImageIOSchema):
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

    attachments_bioimageio_description = (
        "Dictionary of text keys and URI (or a list of URI) values to additional, relevant files. E.g. we can "
        "place a list of URIs under the `files` to list images and other files that this resource depends on."
    )  # todo: shouldn't we package all attachments (or None) and always package certain fields if present?

    attachments = fields.Dict(
        fields.String,
        fields.List(
            fields.Union([fields.URI(), fields.Raw()]),
            bioimageio_maybe_required=True,
            bioimageio_description=attachments_bioimageio_description,
        ),
    )

    authors_bioimageio_description = (
        "A list of authors. The authors are the creators of the specifications and the primary " "points of contact."
    )
    authors = fields.List(
        fields.Union([fields.Nested(Author), fields.String()]), bioimageio_description=authors_bioimageio_description
    )

    badges = fields.List(fields.Nested(Badge), bioimageio_description="a list of badges")

    cite_bioimageio_description = """A citation entry or list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used."""
    cite = fields.Nested(CiteEntry, many=True, required=True, bioimageio_description=cite_bioimageio_description)

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
        "    If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`."
    )
    config = fields.YamlDict(bioimageio_descriptio=config_bioimageio_description)

    covers = fields.List(
        fields.Union(
            [fields.URI(validate=field_validators.URL(schemes=["http", "https"])), fields.RelativeLocalPath()]
        ),
        bioimageio_description="A list of cover images provided by either a relative path to the model folder, or a "
        "hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height "
        "of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.",  # todo: field_validators image format
    )

    description = fields.String(required=True, bioimageio_description="A string containing a brief description.")

    documentation = fields.RelativeLocalPath(
        validate=field_validators.Attribute(
            "suffix",
            field_validators.Equal(".md", error="{!r} is invalid; expected markdown file with '.md' extension."),
        ),
        required=True,
        bioimageio_description="Relative path to file with additional documentation in markdown. This means: 1) only "
        "relative file path is allowed 2) the file must be in markdown format with `.md` file name extension 3) URL is "
        "not allowed. It is recommended to use `README.md` as the documentation name.",
    )

    download_url = fields.String(
        validate=field_validators.URL(schemes=["http", "https"]),
        bioimageio_description="recommended url to the zipped file if applicable",
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
        format_version = data["format_version"]
        type_ = data["type"]
        try:
            patched_format_version = get_patched_format_version(type_, format_version)
            if format_version.split(".") > patched_format_version.split("."):
                raise ValueError(
                    f"Unknown format_version {format_version} (latest patch: {patched_format_version}; latest format version: )"
                )
        except Exception as e:
            raise ValidationError(f"Invalid format_version {format_version} for RDF type {type_}. (error: {e})")

    git_repo_bioimageio_description = "A url to the git repository, e.g. to Github or Gitlab."
    git_repo = fields.String(
        validate=field_validators.URL(schemes=["http", "https"]), bioimageio_description=git_repo_bioimageio_description
    )

    icon = fields.String(
        bioimageio_description="an icon for the resource"
    )  # todo: limit length? validate=field_validators.Length(max=1)

    license_bioimageio_description = (
        "A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, "
        "`BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send "
        "an Github issue to discuss your intentions with the community."
    )
    license = fields.String(
        # validate=field_validators.OneOf(LICENSES),  # only warn for now (see warn_about_deprecated_spdx_license) todo: enforce in 0.4.0
        bioimageio_description=license_bioimageio_description
    )

    @validates("license")
    def warn_about_deprecated_spdx_license(self, value: str):
        license_info = LICENSES.get(value)
        if license_info is None:
            warnings.warn(f"{value} is not a recognized SPDX license identifier. See https://spdx.org/licenses/")
        elif license_info["isDeprecatedLicenseId"]:
            warnings.warn(f"{license_info['name']} is deprecated")

    links = fields.List(fields.String, bioimageio_description="links to other bioimage.io resources")

    name = fields.String(required=True, bioimageio_description="name of the resource, a human-friendly name")

    source = fields.Union(
        [fields.URI(), fields.RelativeLocalPath()],
        bioimageio_description="url or local relative path to the source of the resource",
    )

    tags = fields.List(fields.String, required=True, bioimageio_description="A list of tags.")

    type = fields.String(required=True)

    # todo: restrict valid RDF types (0.4.0)
    # @validates("type")
    # def validate_type(self, value):
    #     schema_type = self.__class__.__name__.lower()
    #     if value != schema_type:
    #         raise ValidationError(f"type must be {schema_type}. Are you using the correct validator?")

    version = fields.StrictVersion(
        bioimageio_description="The version number of the model. The version number format must be a string in "
        "`MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), "
        "e.g. the initial version number should be `0.1.0`."
    )


# todo: decide on Collection/move Collection
# Collection
class CollectionEntry(BioImageIOSchema):
    """instead of nesting RDFs, RDFs can be pointed to"""

    source = fields.URI(validate=field_validators.URL(schemes=["http", "https"]), required=True)
    id = fields.String(required=True)
    links = fields.List(fields.String())


class ModelCollectionEntry(CollectionEntry):
    download_url = fields.URI(validate=field_validators.URL(schemes=["http", "https"]))


class Collection(RDF):
    application = fields.List(fields.Union([fields.Nested(CollectionEntry), fields.Nested(RDF)]))
    collection = fields.List(fields.Union([fields.Nested(CollectionEntry), fields.Nested(RDF)]))
    model = fields.List(fields.Nested(ModelCollectionEntry))
    dataset = fields.List(fields.Union([fields.Nested(CollectionEntry), fields.Nested(RDF)]))
    notebook = fields.List(fields.Union([fields.Nested(CollectionEntry), fields.Nested(RDF)]))
