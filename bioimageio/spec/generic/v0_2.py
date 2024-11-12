import string
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

import annotated_types
from annotated_types import Len, LowerCase, MaxLen
from pydantic import (
    EmailStr,
    Field,
    RootModel,
    ValidationInfo,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated, Self, assert_never

from .._internal.common_nodes import Node, ResourceDescrBase
from .._internal.constants import TAG_CATEGORIES
from .._internal.field_warning import as_warning, issue_warning, warn
from .._internal.io import (
    BioimageioYamlContent,
    InPackageIfLocalFileSource,
    WithSuffix,
    YamlValue,
    include_in_package_serializer,
)
from .._internal.io_basics import AbsoluteFilePath as AbsoluteFilePath
from .._internal.type_guards import is_sequence
from .._internal.types import (
    DeprecatedLicenseId,
    FileSource,
    ImportantFileSource,
    LicenseId,
    NotEmpty,
)
from .._internal.types import Doi as Doi
from .._internal.types import OrcidId as OrcidId
from .._internal.types import RelativeFilePath as RelativeFilePath
from .._internal.url import HttpUrl as HttpUrl
from .._internal.validated_string import ValidatedString
from .._internal.validator_annotations import AfterValidator, RestrictCharacters
from .._internal.version_type import Version as Version
from ._v0_2_converter import convert_from_older_format as _convert_from_older_format


class ResourceId(ValidatedString):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
        Annotated[
            NotEmpty[str],
            AfterValidator(str.lower),  # convert upper case on the fly
            RestrictCharacters(string.ascii_lowercase + string.digits + "_-/."),
            annotated_types.Predicate(
                lambda s: not (s.startswith("/") or s.endswith("/"))
            ),
        ]
    ]


KNOWN_SPECIFIC_RESOURCE_TYPES = (
    "application",
    "collection",
    "dataset",
    "model",
    "notebook",
)

VALID_COVER_IMAGE_EXTENSIONS = (
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".tif",
    ".tiff",
)

_WithImageSuffix = WithSuffix(VALID_COVER_IMAGE_EXTENSIONS, case_sensitive=False)
CoverImageSource = Annotated[
    Union[AbsoluteFilePath, RelativeFilePath, HttpUrl],
    Field(union_mode="left_to_right"),
    _WithImageSuffix,
    include_in_package_serializer,
]


class AttachmentsDescr(Node):
    model_config = {**Node.model_config, "extra": "allow"}
    """update pydantic model config to allow additional unknown keys"""
    files: List[ImportantFileSource] = Field(default_factory=list)
    """∈📦 File attachments"""


def _remove_slashes(s: str):
    return s.replace("/", "").replace("\\", "")


class Uploader(Node):
    email: EmailStr
    """Email"""
    name: Optional[Annotated[str, AfterValidator(_remove_slashes)]] = None
    """name"""


class _Person(Node):
    affiliation: Optional[str] = None
    """Affiliation"""

    email: Optional[EmailStr] = None
    """Email"""

    orcid: Annotated[Optional[OrcidId], Field(examples=["0000-0001-2345-6789"])] = None
    """An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
    ) in hyphenated groups of 4 digits, (and [valid](
    https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
    ) as per ISO 7064 11,2.)
    """


class Author(_Person):
    name: Annotated[str, AfterValidator(_remove_slashes)]
    github_user: Optional[str] = None  # TODO: validate github_user


class Maintainer(_Person):
    name: Optional[Annotated[str, AfterValidator(_remove_slashes)]] = None
    github_user: str


class BadgeDescr(Node, title="Custom badge"):
    """A custom badge"""

    label: Annotated[str, Field(examples=["Open in Colab"])]
    """badge label to display on hover"""

    icon: Annotated[
        Optional[InPackageIfLocalFileSource],
        Field(examples=["https://colab.research.google.com/assets/colab-badge.svg"]),
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

    doi: Optional[Doi] = None
    """A digital object identifier (DOI) is the prefered citation reference.
    See https://www.doi.org/ for details. (alternatively specify `url`)"""

    @field_validator("doi", mode="before")
    @classmethod
    def accept_prefixed_doi(cls, doi: Any) -> Any:
        if isinstance(doi, str):
            for doi_prefix in ("https://doi.org/", "http://dx.doi.org/"):
                if doi.startswith(doi_prefix):
                    doi = doi[len(doi_prefix) :]
                    break

        return doi

    url: Optional[str] = None
    """URL to cite (preferably specify a `doi` instead)"""

    @model_validator(mode="after")
    def _check_doi_or_url(self) -> Self:
        if not self.doi and not self.url:
            raise ValueError("Either 'doi' or 'url' is required")

        return self


class LinkedResource(Node):
    """Reference to a bioimage.io resource"""

    id: ResourceId
    """A valid resource `id` from the bioimage.io collection."""

    version_number: Optional[int] = None
    """version number (n-th published version, not the semantic version) of linked resource"""


class GenericModelDescrBase(ResourceDescrBase):
    """Base for all resource descriptions including of model descriptions"""

    name: Annotated[NotEmpty[str], warn(MaxLen(128), "Longer than 128 characters.")]
    """A human-friendly name of the resource description"""

    description: str

    covers: Annotated[
        List[CoverImageSource],
        Field(
            examples=["cover.png"],
            description=(
                "Cover images. Please use an image smaller than 500KB and an aspect"
                " ratio width to height of 2:1.\nThe supported image formats are:"
                f" {VALID_COVER_IMAGE_EXTENSIONS}"
            ),
        ),
    ] = Field(
        default_factory=list,
    )
    """∈📦 Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1."""

    id_emoji: Optional[Annotated[str, Len(min_length=1, max_length=1)]] = None
    """UTF-8 emoji for display alongside the `id`."""

    authors: List[Author] = Field(default_factory=list)
    """The authors are the creators of the RDF and the primary points of contact."""

    @field_validator("authors", mode="before")
    @classmethod
    def accept_author_strings(cls, authors: Union[Any, Sequence[Any]]) -> Any:
        """we unofficially accept strings as author entries"""
        if is_sequence(authors):
            authors = [{"name": a} if isinstance(a, str) else a for a in authors]

        if not authors:
            issue_warning("missing", value=authors, field="authors")

        return authors

    attachments: Optional[AttachmentsDescr] = None
    """file and other attachments"""

    cite: List[CiteEntry] = Field(default_factory=list)
    """citations"""

    @field_validator("cite", mode="after")
    @classmethod
    def _warn_empty_cite(cls, value: Any):
        if not value:
            issue_warning("missing", value=value, field="cite")

        return value

    config: Annotated[
        Dict[str, YamlValue],
        Field(
            examples=[
                dict(
                    bioimageio={
                        "my_custom_key": 3837283,
                        "another_key": {"nested": "value"},
                    },
                    imagej={"macro_dir": "path/to/macro/file"},
                )
            ],
        ),
    ] = Field(default_factory=dict)
    """A field for custom configuration that can contain any keys not present in the RDF spec.
    This means you should not store, for example, a github repo URL in `config` since we already have the
    `git_repo` field defined in the spec.
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
    You may want to list linked files additionally under `attachments` to include them when packaging a resource
    (packaging a resource means downloading/copying important linked files and creating a ZIP archive that contains
    an altered rdf.yaml file with local references to the downloaded files)"""

    download_url: Optional[HttpUrl] = None
    """URL to download the resource from (deprecated)"""

    git_repo: Annotated[
        Optional[str],
        Field(
            examples=[
                "https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad"
            ],
        ),
    ] = None
    """A URL to the Git repository where the resource is being developed."""

    icon: Union[
        Annotated[str, Len(min_length=1, max_length=2)], ImportantFileSource, None
    ] = None
    """An icon for illustration"""

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
    If not specified `authors` are maintainers and at least some of them should specify their `github_user` name"""

    rdf_source: Optional[FileSource] = None
    """Resource description file (RDF) source; used to keep track of where an rdf.yaml was loaded from.
    Do not set this field in a YAML file."""

    tags: Annotated[
        List[str],
        Field(examples=[("unet2d", "pytorch", "nucleus", "segmentation", "dsb2018")]),
    ] = Field(default_factory=list)
    """Associated tags"""

    @as_warning
    @field_validator("tags")
    @classmethod
    def warn_about_tag_categories(
        cls, value: List[str], info: ValidationInfo
    ) -> List[str]:
        categories = TAG_CATEGORIES.get(info.data["type"], {})
        missing_categories: List[Mapping[str, Sequence[str]]] = []
        for cat, entries in categories.items():
            if not any(e in value for e in entries):
                missing_categories.append({cat: entries})

        if missing_categories:
            raise ValueError(
                "Missing tags from bioimage.io categories: {missing_categories}"
            )

        return value

    version: Optional[Version] = None
    """The version of the resource following SemVer 2.0."""

    version_number: Optional[int] = None
    """version number (n-th published version, not the semantic version)"""


class GenericDescrBase(GenericModelDescrBase):
    """Base for all resource descriptions except for the model descriptions"""

    format_version: Literal["0.2.4"] = "0.2.4"
    """The format version of this resource specification
    (not the `version` of the resource description)
    When creating a new resource always use the latest micro/patch version described here.
    The `format_version` is important for any consumer software to understand how to parse the fields.
    """

    @model_validator(mode="before")
    @classmethod
    def _convert_from_older_format(
        cls, data: BioimageioYamlContent, /
    ) -> BioimageioYamlContent:
        _convert_from_older_format(data)
        return data

    badges: List[BadgeDescr] = Field(default_factory=list)
    """badges associated with this resource"""

    documentation: Annotated[
        Optional[ImportantFileSource],
        Field(
            examples=[
                "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md",
                "README.md",
            ],
        ),
    ] = None
    """∈📦 URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory."""

    license: Annotated[
        Union[LicenseId, DeprecatedLicenseId, str, None],
        Field(union_mode="left_to_right", examples=["CC0-1.0", "MIT", "BSD-2-Clause"]),
    ] = None
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do not support custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose
    ) to discuss your intentions with the community."""

    @field_validator("license", mode="after")
    @classmethod
    def deprecated_spdx_license(
        cls, value: Optional[Union[LicenseId, DeprecatedLicenseId, str]]
    ):
        if isinstance(value, LicenseId):
            pass
        elif value is None:
            issue_warning("missing", value=value, field="license")
        elif isinstance(value, DeprecatedLicenseId):
            issue_warning(
                "'{value}' is a deprecated license identifier.",
                value=value,
                field="license",
            )
        elif isinstance(value, str):
            issue_warning(
                "'{value}' is an unknown license identifier.",
                value=value,
                field="license",
            )
        else:
            assert_never(value)

        return value


ResourceDescrType = TypeVar("ResourceDescrType", bound=GenericDescrBase)


class GenericDescr(
    GenericDescrBase, extra="ignore", title="bioimage.io generic specification"
):
    """Specification of the fields used in a generic bioimage.io-compliant resource description file (RDF).

    An RDF is a YAML file that describes a resource such as a model, a dataset, or a notebook.
    Note that those resources are described with a type-specific RDF.
    Use this generic resource description, if none of the known specific types matches your resource.
    """

    type: Annotated[str, LowerCase, Field(frozen=True)] = "generic"
    """The resource type assigns a broad category to the resource."""

    id: Optional[ResourceId] = None
    """bioimage.io-wide unique resource identifier
    assigned by bioimage.io; version **un**specific."""

    source: Optional[HttpUrl] = None
    """The primary source of the resource"""

    @field_validator("type", mode="after")
    @classmethod
    def check_specific_types(cls, value: str) -> str:
        if value in KNOWN_SPECIFIC_RESOURCE_TYPES:
            raise ValueError(
                f"Use the {value} description instead of this generic description for"
                + f" your '{value}' resource."
            )

        return value
