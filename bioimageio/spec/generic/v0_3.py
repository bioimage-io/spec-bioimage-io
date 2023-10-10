from functools import partial
from typing import List, Literal, Mapping, Optional, Sequence, Tuple, TypeVar, Union

from annotated_types import Len, LowerCase, MaxLen
from pydantic import Field, FieldValidationInfo, field_validator
from pydantic import HttpUrl as HttpUrl
from typing_extensions import Annotated

from bioimageio.spec._internal.base_nodes import ConfigNode, Node, ResourceDescriptionBase
from bioimageio.spec._internal.constants import ALERT, LICENSES, TAG_CATEGORIES
from bioimageio.spec._internal.field_warning import as_warning, warn
from bioimageio.spec._internal.types import (
    DeprecatedLicenseId,
    FileSource,
    LicenseId,
    NonEmpty,
    RdfContent,
    ResourceId,
    Sha256,
    Version,
)
from bioimageio.spec._internal.types import RelativeFilePath as RelativeFilePath
from bioimageio.spec._internal.types.field_validation import WithSuffix
from bioimageio.spec._internal.validation_context import InternalValidationContext
from bioimageio.spec.generic.v0_2 import VALID_COVER_IMAGE_EXTENSIONS
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import Badge as Badge
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3_converter import convert_from_older_format

KNOWN_SPECIFIC_RESOURCE_TYPES = ("application", "collection", "dataset", "model", "notebook")


class Attachment(Node, frozen=True):
    source: FileSource
    """∈📦 """
    sha256: Annotated[Optional[Sha256], warn(Sha256, "Missing SHA-256 hash value.")] = None


class LinkedResource(Node, frozen=True):
    """Reference to a bioimage.io resource"""

    id: ResourceId
    """A valid resource `id` from the official bioimage.io collection."""


class GenericBaseNoSource(ResourceDescriptionBase, frozen=True):
    """GenericBaseNoFormatVersion without a source field

    (because `bioimageio.spec.model.v0_5.ModelDescription has no source field)
    """

    format_version: str
    """The format version of this resource specification
    (not the `version` of the resource description)"""

    name: Annotated[NonEmpty[str], MaxLen(128)]
    """A human-friendly name of the resource description"""

    description: Annotated[str, MaxLen(1024), warn(MaxLen(512), "Description longer than 512 characters.")]
    """A string containing a brief description."""

    documentation: Annotated[
        Optional[Annotated[FileSource, WithSuffix(".md", case_sensitive=True)]],
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
            examples=[],
            description=(
                "Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.\n"
                f"The supported image formats are: {VALID_COVER_IMAGE_EXTENSIONS}"
            ),
        ),
    ] = ()
    """∈📦 Cover images."""

    id: Optional[ResourceId] = None
    """bioimage.io wide, unique identifier assigned by the
    [bioimage.io collection](https://github.com/bioimage-io/collection-bioimage-io)"""

    authors: NonEmpty[Tuple[Author, ...]]
    """The authors are the creators of the RDF and the primary points of contact."""

    attachments: Tuple[Attachment, ...] = ()
    """file and other attachments"""

    badges: Tuple[Badge, ...] = ()
    """badges associated with this resource"""

    cite: NonEmpty[Tuple[CiteEntry, ...]]
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
    This means you should not store, for example, a GitHub repo URL in `config` since there is a `git_repo` field.
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
    You may want to list linked files additionally under `attachments` to include them when packaging a resource.
    (Packaging a resource means downloading/copying important linked files and creating a ZIP archive that contains
    an altered rdf.yaml file with local references to the downloaded files.)"""

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
    """An icon for illustration, e.g. on bioimage.io"""

    license: Annotated[
        Union[LicenseId, Annotated[DeprecatedLicenseId, "deprecated"]],
        warn(LicenseId, "'{value}' is a deprecated or unknown license identifier."),
        Field(examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"]),
    ]
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
    If not specified, `authors` are maintainers and at least some of them has to specify their `github_user` name"""

    @partial(as_warning, severity=ALERT)
    @field_validator("maintainers", mode="after")
    @classmethod
    def check_maintainers_exist(
        cls, maintainers: Tuple[Maintainer, ...], info: FieldValidationInfo
    ) -> Tuple[Maintainer, ...]:
        if not maintainers and "authors" in info.data:
            authors: Tuple[Author, ...] = info.data["authors"]
            if all(a.github_user is None for a in authors):
                raise ValueError(
                    "Missing `maintainers` or any author in `authors` with a specified `github_user` name."
                )

        return maintainers

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
    def convert_from_older_format(cls, data: RdfContent, context: InternalValidationContext) -> None:
        """convert raw RDF data of an older format where possible"""
        super().convert_from_older_format(data, context)
        convert_from_older_format(data, context)


ResourceDescriptionType = TypeVar("ResourceDescriptionType", bound=GenericBaseNoSource)


class GenericBaseNoFormatVersion(GenericBaseNoSource, frozen=True):
    """GenericBase without a format version"""

    source: Optional[FileSource] = None
    """The primary source of the resource"""


class GenericBase(GenericBaseNoFormatVersion, frozen=True, extra="ignore"):
    format_version: Literal["0.3.0"] = "0.3.0"


class Generic(GenericBase, frozen=True, title="bioimage.io generic specification"):
    """Specification of the fields used in a generic bioimage.io-compliant resource description file (RDF).

    An RDF is a YAML file that describes a resource such as a model, a dataset, or a notebook.
    Note that those resources are described with a type-specific RDF.
    Use this generic resource description, if none of the known specific types matches your resource.
    """

    type: Annotated[str, LowerCase] = "generic"
    """The resource type assigns a broad category to the resource."""

    @field_validator("type", mode="after")
    @classmethod
    def check_specific_types(cls, value: str) -> str:
        if value in KNOWN_SPECIFIC_RESOURCE_TYPES:
            raise ValueError(
                f"Use the {value} description instead of this generic description for your '{value}' resource."
            )

        return value
