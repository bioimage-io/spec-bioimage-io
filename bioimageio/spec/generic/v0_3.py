from __future__ import annotations

from functools import partial
from typing import Any, Dict, List, Literal, Optional, Sequence, TypeVar, Union

import requests
from annotated_types import Ge, Len, LowerCase, MaxLen
from pydantic import Field, ValidationInfo, field_validator, model_validator
from typing_extensions import Annotated

from bioimageio.spec._internal import settings
from bioimageio.spec._internal.base_nodes import Converter, Node, ResourceDescriptionBase
from bioimageio.spec._internal.base_nodes import FileDescr as FileDescr
from bioimageio.spec._internal.constants import (
    ALERT,
    LICENSES,
    TAG_CATEGORIES,
)
from bioimageio.spec._internal.field_warning import as_warning, issue_warning, warn
from bioimageio.spec._internal.types import (
    AbsoluteFilePath,
    BioimageioYamlContent,
    DeprecatedLicenseId,
    ImportantFileSource,
    IncludeInPackage,
    LicenseId,
    NotEmpty,
    YamlValue,
)
from bioimageio.spec._internal.types import HttpUrl as HttpUrl
from bioimageio.spec._internal.types import RelativeFilePath as RelativeFilePath
from bioimageio.spec._internal.types import ResourceId as ResourceId
from bioimageio.spec._internal.types import Sha256 as Sha256
from bioimageio.spec._internal.types.field_validation import Predicate, WithSuffix
from bioimageio.spec._internal.validation_context import validation_context_var
from bioimageio.spec.generic import v0_2
from bioimageio.spec.generic._v0_3_converter import convert_from_older_format
from bioimageio.spec.generic.v0_2 import VALID_COVER_IMAGE_EXTENSIONS, CoverImageSource
from bioimageio.spec.generic.v0_2 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import Doi as Doi
from bioimageio.spec.generic.v0_2 import OrcidId as OrcidId
from bioimageio.spec.generic.v0_2 import Uploader as Uploader

KNOWN_SPECIFIC_RESOURCE_TYPES = ("application", "collection", "dataset", "model", "notebook")


_WithMdSuffix = WithSuffix(".md", case_sensitive=True)
MarkdownSource = Union[
    Annotated[HttpUrl, _WithMdSuffix],
    Annotated[AbsoluteFilePath, _WithMdSuffix],
    Annotated[RelativeFilePath, _WithMdSuffix],
]
DocumentationSource = Annotated[MarkdownSource, IncludeInPackage()]


def _has_no_slash(s: str) -> bool:
    return "/" not in s and "\\" not in s


def _validate_gh_user(username: str):
    if not validation_context_var.get().perform_io_checks:
        return

    r = requests.get(f"https://api.github.com/users/{username}", auth=settings.github_auth)
    if r.status_code == 403 and r.reason == "rate limit exceeded":
        issue_warning("Could not verify GitHub user '{value}' due to GitHub API rate limit", value=username)
    elif r.status_code != 200:
        raise ValueError(f"Could not find GitHub user '{username}'")


class Author(v0_2.Author):
    name: Annotated[str, Predicate(_has_no_slash)]
    github_user: Optional[str] = None

    @field_validator("github_user", mode="after")
    def validate_gh_user(cls, value: Optional[str]):
        if value is not None:
            _validate_gh_user(value)

        return value


class _AuthorConv(Converter[v0_2.Author, Author]):
    def _convert(self, src: v0_2.Author, tgt: "type[Author] | type[dict[str, Any]]") -> "Author | dict[str, Any]":
        return tgt(
            name=src.name,
            github_user=src.github_user,
            affiliation=src.affiliation,
            email=src.email,
            orcid=src.orcid,
        )


_author_conv = _AuthorConv(v0_2.Author, Author)


class Maintainer(v0_2.Maintainer):
    name: Optional[Annotated[str, Predicate(_has_no_slash)]] = None
    github_user: str

    @field_validator("github_user", mode="after")
    def validate_gh_user(cls, value: str):
        _validate_gh_user(value)
        return value


class _MaintainerConv(Converter[v0_2.Maintainer, Maintainer]):
    def _convert(self, src: v0_2.Maintainer, tgt: "type[Maintainer | dict[str, Any]]") -> "Maintainer | dict[str, Any]":
        return tgt(
            name=src.name,
            github_user=src.github_user,
            affiliation=src.affiliation,
            email=src.email,
            orcid=src.orcid,
        )


_maintainer_conv = _MaintainerConv(v0_2.Maintainer, Maintainer)


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

    id_emoji: Optional[Annotated[str, Len(min_length=1, max_length=1)]] = None
    """UTF-8 emoji for display alongside the `id`."""

    authors: NotEmpty[List[Author]]
    """The authors are the creators of this resource description and the primary points of contact."""

    attachments: List[FileDescr] = Field(default_factory=list)
    """file attachments"""

    cite: NotEmpty[List[CiteEntry]]
    """citations"""

    config: Annotated[
        Dict[str, YamlValue],
        Field(
            examples=[
                dict(
                    bioimageio={"my_custom_key": 3837283, "another_key": {"nested": "value"}},
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
        bioimageio:  # here is the domain name
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

    icon: Union[ImportantFileSource, Annotated[str, Len(min_length=1, max_length=2)], None] = None
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

    uploader: Optional[Uploader] = None
    """The person who uploaded the model (e.g. to bioimage.io)"""

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

    version: Annotated[int, Ge(ge=1), Field(examples=[1, 2, 3])] = 1
    """The version number of the resource."""


class GenericDescrBase(GenericModelDescrBase):
    """Base for all resource descriptions except for the model descriptions"""

    format_version: Literal["0.3.0"] = "0.3.0"
    """The **format** version of this resource specification"""

    @model_validator(mode="before")
    @classmethod
    def _convert_from_older_format(cls, data: BioimageioYamlContent, /) -> BioimageioYamlContent:
        convert_from_older_format(data)
        return data

    documentation: Annotated[
        Optional[DocumentationSource],
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
        Field(examples=["CC-BY-4.0", "MIT", "BSD-2-Clause"]),
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
