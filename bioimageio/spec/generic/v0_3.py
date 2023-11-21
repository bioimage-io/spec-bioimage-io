from functools import partial
from typing import Any, Dict, List, Literal, Optional, Sequence, TypeVar, Union

from annotated_types import Len, LowerCase, MaxLen
from pydantic import Field, ValidationInfo, field_validator
from typing_extensions import Annotated

from bioimageio.spec._internal.base_nodes import FileDescr as FileDescr
from bioimageio.spec._internal.base_nodes import Node, ResourceDescriptionBase
from bioimageio.spec._internal.constants import ALERT, LICENSES, TAG_CATEGORIES
from bioimageio.spec._internal.field_warning import as_warning, warn
from bioimageio.spec._internal.types import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec._internal.types import (
    BioimageioYamlContent,
    DeprecatedLicenseId,
    LicenseId,
    NotEmpty,
    Version,
)
from bioimageio.spec._internal.types import FileSource as FileSource
from bioimageio.spec._internal.types import HttpUrl as HttpUrl
from bioimageio.spec._internal.types import RelativeFilePath as RelativeFilePath
from bioimageio.spec._internal.types import ResourceId as ResourceId
from bioimageio.spec._internal.types import Sha256 as Sha256
from bioimageio.spec._internal.types.field_validation import WithSuffix
from bioimageio.spec._internal.validation_context import InternalValidationContext
from bioimageio.spec.generic.v0_2 import VALID_COVER_IMAGE_EXTENSIONS, CoverImageSource
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import Doi as Doi
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3_converter import convert_from_older_format

KNOWN_SPECIFIC_RESOURCE_TYPES = ("application", "collection", "dataset", "model", "notebook")


_WithMdSuffix = WithSuffix(".md", case_sensitive=True)
MarkdownSource = Union[
    Annotated[HttpUrl, _WithMdSuffix],
    Annotated[AbsoluteFilePath, _WithMdSuffix],
    Annotated[RelativeFilePath, _WithMdSuffix],
]


class LinkedResourceDescr(Node):
    """Reference to a bioimage.io resource"""

    id: ResourceId
    """A valid resource `id` from the official bioimage.io collection."""


class GenericModelDescrBase(ResourceDescriptionBase):
    """Base for all resource descriptions including of model descriptions"""

    name: Annotated[NotEmpty[str], MaxLen(128)]
    """A human-friendly name of the resource description"""

    description: Annotated[str, MaxLen(1024), warn(MaxLen(512), "Description longer than 512 characters.")]
    """A string containing a brief description."""

    covers: Annotated[
        List[CoverImageSource],
        Field(
            examples=[],
            description=(
                "Cover images. "
                "Please use an image smaller than 500KB and an aspect ratio width to height of 2:1 or 1:1.\n"
                f"The supported image formats are: {VALID_COVER_IMAGE_EXTENSIONS}"
            ),
        ),
    ] = Field(default_factory=list)
    """∈📦 Cover images."""

    id: Optional[ResourceId] = None
    """bioimage.io wide, unique identifier assigned by the
    [bioimage.io collection](https://github.com/bioimage-io/collection-bioimage-io)"""

    authors: NotEmpty[List[Author]]
    """The authors are the creators of the RDF and the primary points of contact."""

    attachments: List[FileDescr] = Field(default_factory=list)
    """file attachments"""

    cite: NotEmpty[List[CiteEntry]]
    """citations"""

    config: Annotated[
        Dict[str, Any],
        Field(
            examples=[
                dict(
                    bioimage_io={"my_custom_key": 3837283, "another_key": {"nested": "value"}},
                    imagej={"macro_dir": "path/to/macro/file"},
                )
            ],
        ),
    ] = Field(default_factory=dict)
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
        Optional[HttpUrl],
        Field(
            examples=[
                "https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_specs/models/unet2d_nuclei_broad"
            ],
        ),
    ] = None
    """A URL to the Git repository where the resource is being developed."""

    icon: Union[FileSource, Annotated[str, Len(min_length=1, max_length=2)], None] = None
    """An icon for illustration, e.g. on bioimage.io"""

    @as_warning
    @field_validator("license", mode="after")
    @classmethod
    def deprecated_spdx_license(cls, value: Optional[str]) -> Optional[str]:
        license_info = LICENSES[value] if value in LICENSES else {}
        if not license_info.get("isFsfLibre", False):
            raise ValueError(f"{value} ({license_info['name']}) is not FSF Free/libre.")

        return value

    links: Annotated[
        List[str],
        Field(
            examples=[
                (
                    "ilastik/ilastik",
                    "deepimagej/deepimagej",
                    "zero/notebook_u-net_3d_zerocostdl4mic",
                )
            ],
        ),
    ] = Field(default_factory=list)
    """IDs of other bioimage.io resources"""

    maintainers: List[Maintainer] = Field(default_factory=list)
    """Maintainers of this resource.
    If not specified, `authors` are maintainers and at least some of them has to specify their `github_user` name"""

    @partial(as_warning, severity=ALERT)
    @field_validator("maintainers", mode="after")
    @classmethod
    def check_maintainers_exist(cls, maintainers: List[Maintainer], info: ValidationInfo) -> List[Maintainer]:
        if not maintainers and "authors" in info.data:
            authors: List[Author] = info.data["authors"]
            if all(a.github_user is None for a in authors):
                raise ValueError(
                    "Missing `maintainers` or any author in `authors` with a specified `github_user` name."
                )

        return maintainers

    tags: Annotated[List[str], Field(examples=[("unet2d", "pytorch", "nucleus", "segmentation", "dsb2018")])] = Field(
        default_factory=list
    )
    """Associated tags"""

    @as_warning
    @field_validator("tags")
    @classmethod
    def warn_about_tag_categories(cls, value: List[str], info: ValidationInfo) -> List[str]:
        categories = TAG_CATEGORIES.get(info.data["type"], {})
        missing_categories: List[Dict[str, Sequence[str]]] = []
        for cat, entries in categories.items():
            if not any(e in value for e in entries):
                missing_categories.append({cat: entries})

        if missing_categories:
            raise ValueError(f"Missing tags from bioimage.io categories: {missing_categories}")

        return value

    version: Annotated[Optional[Version], Field(examples=["0.1.0"])] = None
    """The version number of the resource. Its format must be a string in
    `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/).
    Hyphens and plus signs are not allowed to be compatible with
    https://packaging.pypa.io/en/stable/version.html.
    The initial version should be '0.1.0'."""


class GenericDescrBase(GenericModelDescrBase):
    """Base for all resource descriptions except for the model descriptions"""

    format_version: Literal["0.3.0"] = "0.3.0"
    """The **format** version of this resource specification"""

    @classmethod
    def convert_from_older_format(cls, data: BioimageioYamlContent, context: InternalValidationContext) -> None:
        convert_from_older_format(data, context)

    documentation: Annotated[
        Optional[MarkdownSource],
        Field(
            examples=[
                "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/README.md",
                "README.md",
            ],
        ),
    ] = None
    """∈📦 URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory."""

    license: Annotated[
        Union[LicenseId, Annotated[DeprecatedLicenseId, "deprecated"]],
        warn(LicenseId, "'{value}' is a deprecated or unknown license identifier."),
        Field(examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"]),
    ]
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do not support custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose
    ) to discuss your intentions with the community."""

    badges: List[BadgeDescr] = Field(default_factory=list)
    """badges associated with this resource"""


ResourceDescrType = TypeVar("ResourceDescrType", bound=GenericDescrBase)


class GenericDescr(GenericDescrBase, extra="ignore", title="bioimage.io generic specification"):
    """Specification of the fields used in a generic bioimage.io-compliant resource description file (RDF).

    An RDF is a YAML file that describes a resource such as a model, a dataset, or a notebook.
    Note that those resources are described with a type-specific RDF.
    Use this generic resource description, if none of the known specific types matches your resource.
    """

    type: Annotated[str, LowerCase] = Field("generic", frozen=True)
    """The resource type assigns a broad category to the resource."""

    source: Optional[HttpUrl] = None
    """The primary source of the resource"""

    @field_validator("type", mode="after")
    @classmethod
    def check_specific_types(cls, value: str) -> str:
        if value in KNOWN_SPECIFIC_RESOURCE_TYPES:
            raise ValueError(
                f"Use the {value} description instead of this generic description for your '{value}' resource."
            )

        return value
