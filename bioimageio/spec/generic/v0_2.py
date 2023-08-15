from collections.abc import Mapping, Sequence
from typing import List, Literal, Optional, Tuple, TypeVar, Union, get_args

from annotated_types import Len, LowerCase, MaxLen, MinLen
from pydantic import (
    ConfigDict,
    EmailStr,
    Field,
    FieldValidationInfo,
    HttpUrl,
    StringConstraints,
    field_validator,
)
from typing_extensions import Annotated

from bioimageio.spec._internal._constants import DOI_REGEX, LICENSES, TAG_CATEGORIES, WARNING
from bioimageio.spec._internal._validate import WithSuffix
from bioimageio.spec._internal._warn import (
    as_warning,
    warn,
)
from bioimageio.spec.generic.v0_2_converter import convert_from_older_format
from bioimageio.spec.shared.nodes import ConfigNode, Node, ResourceDescriptionBase
from bioimageio.spec.shared.types import (
    DeprecatedLicenseId,
    FileSource,
    LicenseId,
    NonEmpty,
    OrcidId,
    RawDict,
    Version,
)
from bioimageio.spec._internal._validate import ValContext

SpecificResourceType = Literal["application", "collection", "dataset", "model", "notebook"]

VALID_COVER_IMAGE_EXTENSIONS = (
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
)


class Attachments(Node):
    model_config = {**Node.model_config, "extra": "allow"}
    """update pydantic model config to allow additional unknown keys"""
    files: Tuple[FileSource, ...] = ()
    """∈📦 File attachments"""


class Person(Node):
    name: Optional[str]
    """Full name"""
    affiliation: Optional[str] = None
    """Affiliation"""
    email: Optional[EmailStr] = None
    """Email"""
    github_user: Optional[str]
    """GitHub user name"""
    orcid: Annotated[Optional[OrcidId], Field(examples=["0000-0001-2345-6789"])] = None
    """An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
    ) in hyphenated groups of 4 digits, (and [valid](
    https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
    ) as per ISO 7064 11,2.)
    """


class Author(Person):
    name: str
    github_user: Optional[str] = None


class Maintainer(Person):
    name: Optional[str] = None
    github_user: str


class Badge(Node, title="Custom badge"):
    """A custom badge"""

    label: Annotated[str, Field(examples=["Open in Colab"])]
    """badge label to display on hover"""

    icon: Annotated[
        Union[HttpUrl, None], Field(examples=["https://colab.research.google.com/assets/colab-badge.svg"])
    ] = None
    """badge icon"""

    url: Annotated[
        HttpUrl,
        Field(
            examples=[
                "https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb"
            ]
        ),
    ]
    """target URL"""


class CiteEntry(Node):
    text: str
    """free text description"""

    doi: Optional[Annotated[str, StringConstraints(pattern=DOI_REGEX)]] = None
    """A digital object identifier (DOI) is the prefered citation reference.
    See https://www.doi.org/ for details. (alternatively specify `url`)"""

    url: Optional[str] = None
    """URL to cite (preferably specify a `doi` instead)"""

    @field_validator("url", mode="after")
    @classmethod
    def check_doi_or_url(cls, value: Optional[str], info: FieldValidationInfo) -> Optional[str]:
        no_error_for_doi = "doi" in info.data
        if no_error_for_doi and not info.data["doi"] and not value:
            raise ValueError("Either 'doi' or 'url' is required")

        return value


class LinkedResource(Node):
    """Reference to a bioimage.io resource"""

    id: NonEmpty[str]
    """A valid resource `id` from the bioimage.io collection."""


class GenericBaseNoSource(ResourceDescriptionBase):
    """GenericBaseNoFormatVersion without a source field

    (needed because `model.v0_4.Model` and `model.v0_5.Model` have no `source` field)
    """

    format_version: str
    """The format version of this resource specification
    (not the `version` of the resource description)
    When creating a new resource always use the latest micro/patch version described here.
    The `format_version` is important for any consumer software to understand how to parse the fields.
    """

    name: Annotated[NonEmpty[str], warn(MaxLen(128))]
    """A human-friendly name of the resource description"""

    description: str

    documentation: Annotated[
        Union[FileSource, None],
        Field(
            examples=[
                "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/README.md",
                "README.md",
            ],
        ),
    ] = None
    """∈📦 URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory."""

    covers: Annotated[
        Tuple[Annotated[FileSource, WithSuffix(VALID_COVER_IMAGE_EXTENSIONS, case_sensitive=False)], ...],
        Field(
            examples=["cover.png"],
            description=(
                "Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.\n"
                f"The supported image formats are: {VALID_COVER_IMAGE_EXTENSIONS}"
            ),
        ),
    ] = ()
    """∈📦 Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1."""

    id: Optional[str] = None
    """bioimage.io wide, unique identifier assigned by the [bioimage.io collection](https://github.com/bioimage-io/collection-bioimage-io)"""

    authors: Annotated[Tuple[Author, ...], warn(MinLen(1), WARNING, "Please specify at least one author.")] = ()
    """The authors are the creators of the RDF and the primary points of contact."""

    attachments: Optional[Attachments] = None
    """file and other attachments"""

    badges: Tuple[Badge, ...] = ()
    """badges associated with this resource"""

    cite: Annotated[
        Tuple[CiteEntry, ...],
        warn(MinLen(1), WARNING, "Please specify at least one source to cite."),
    ] = ()
    """citations"""

    config: Annotated[
        ConfigNode,
        Field(
            examples=[
                dict(
                    bioimage_io={"my_custom_key": 3837283, "another_key": {"nested": "value"}},
                    imagej={"macro_dir": "path/to/macro/file"},
                )
            ],
        ),
    ] = ConfigNode()
    """A field for custom configuration that can contain any keys not present in the RDF spec.
    This means you should not store, for example, a github repo URL in `config` since we already have the
    `git_repo` field defined in the spec.
    Keys in `config` may be very specific to a tool or consumer software. To avoid conflicting definitions,
    it is recommended to wrap added configuration into a sub-field named with the specific domain or tool name,
    for example:
    ```yaml
    config:
        bioimage_io:  # here is the domain name
            my_custom_key: 3837283
            another_key:
                nested: value
        imagej:       # config specific to ImageJ
            macro_dir: path/to/macro/file
    ```
    If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.
    You may want to list linked files additionally under `attachments` to include them when packaging a resource
    (packaging a resource means downloading/copying important linked files and creating a ZIP archive that contains
    an altered rdf.yaml file with local references to the downloaded files)"""

    download_url: Optional[HttpUrl] = None
    """URL to download the resource from (deprecated)"""

    git_repo: Annotated[
        Optional[str],
        Field(
            examples=[
                "https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_specs/models/unet2d_nuclei_broad"
            ],
        ),
    ] = None
    """A URL to the Git repository where the resource is being developed."""

    icon: Union[FileSource, Annotated[str, Len(min_length=1, max_length=2)], None] = None
    """An icon for illustration"""

    license: Annotated[
        Union[LicenseId, DeprecatedLicenseId, str, None],
        warn(LicenseId, WARNING, "'{value}' is a deprecated or unknown license identifier."),
        Field(examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"]),
    ] = None
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do not support custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose
    ) to discuss your intentions with the community."""

    @as_warning
    @field_validator("license", mode="after")
    @classmethod
    def deprecated_spdx_license(cls, value: Optional[str]) -> Optional[str]:
        license_info = LICENSES[value] if value in LICENSES else {}
        if not license_info.get("isFsfLibre", False):
            raise ValueError(f"{value} ({license_info['name']}) is not FSF Free/libre.")

        return value

    links: Annotated[
        Tuple[str, ...],
        Field(
            examples=[
                (
                    "ilastik/ilastik",
                    "deepimagej/deepimagej",
                    "zero/notebook_u-net_3d_zerocostdl4mic",
                )
            ],
        ),
    ] = ()
    """IDs of other bioimage.io resources"""

    maintainers: Tuple[Maintainer, ...] = ()
    """Maintainers of this resource.
    If not specified `authors` are maintainers and at least some of them should specify their `github_user` name"""

    rdf_source: Optional[FileSource] = None
    """Resource description file (RDF) source; used to keep track of where an rdf.yaml was downloaded from.
    Do not set this field in a YAML file."""

    tags: Annotated[Tuple[str, ...], Field(examples=[("unet2d", "pytorch", "nucleus", "segmentation", "dsb2018")])] = ()
    """Associated tags"""

    @as_warning
    @field_validator("tags")
    @classmethod
    def warn_about_tag_categories(cls, value: Tuple[str, ...], info: FieldValidationInfo) -> Tuple[str, ...]:
        categories = TAG_CATEGORIES.get(info.data["type"], {})
        missing_categories: List[Mapping[str, Sequence[str]]] = []
        for cat, entries in categories.items():
            if not any(e in value for e in entries):
                missing_categories.append({cat: entries})

        if missing_categories:
            raise ValueError("Missing tags from bioimage.io categories: {missing_categories}")

        return value

    version: Annotated[Optional[Version], Field(examples=["0.1.0"])] = None
    """The version number of the resource. Its format must be a string in
    `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/).
    Hyphens and plus signs are not allowed to be compatible with
    https://packaging.pypa.io/en/stable/version.html.
    The initial version should be '0.1.0'."""

    @classmethod
    def convert_from_older_format(cls, data: RawDict, context: ValContext) -> None:
        """convert raw RDF data of an older format where possible"""
        convert_from_older_format(data, context)


ResourceDescriptionType = TypeVar("ResourceDescriptionType", bound=GenericBaseNoSource)


class GenericBaseNoFormatVersion(GenericBaseNoSource):
    """A generic node base without format version
    to allow a derived resource description to define its format_version independently."""

    source: Annotated[
        Optional[FileSource], Field(description="URL or relative path to the source of the resource")
    ] = None
    """The primary source of the resource"""


class GenericBase(GenericBaseNoFormatVersion):
    format_version: Literal["0.2.3"] = "0.2.3"


class Generic(GenericBase):
    """Specification of the fields used in a generic bioimage.io-compliant resource description file (RDF).

    An RDF is a YAML file that describes a resource such as a model, a dataset, or a notebook.
    Note that those resources are described with a type-specific RDF.
    Use this generic resource description, if none of the known specific types matches your resource.
    """

    model_config = {**GenericBase.model_config, **ConfigDict(title="bioimage.io generic specification", extra="ignore")}
    """pydantic model_config"""

    type: Annotated[str, LowerCase]
    """The resource type assigns a broad category to the resource."""

    @field_validator("type", mode="after")
    @classmethod
    def check_specific_types(cls, value: str) -> str:
        if value in get_args(SpecificResourceType):
            raise ValueError(
                f"Use the {value} description instead of this generic description for your '{value}' resource."
            )

        return value


AnyGeneric = Generic
