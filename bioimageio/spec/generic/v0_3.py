from __future__ import annotations

import string
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
)

import annotated_types
from annotated_types import Len, LowerCase, MaxLen, MinLen
from pydantic import Field, RootModel, ValidationInfo, field_validator, model_validator
from typing_extensions import Annotated

from .._internal.common_nodes import Node, ResourceDescrBase
from .._internal.constants import TAG_CATEGORIES
from .._internal.field_validation import validate_github_user
from .._internal.field_warning import as_warning, issue_warning, warn
from .._internal.io import (
    BioimageioYamlContent,
    FileDescr,
    WithSuffix,
    is_yaml_value,
)
from .._internal.io_basics import Sha256
from .._internal.io_packaging import FileDescr_
from .._internal.license_id import DeprecatedLicenseId, LicenseId
from .._internal.node_converter import Converter
from .._internal.type_guards import is_dict
from .._internal.types import FAIR, FileSource_, NotEmpty, RelativeFilePath
from .._internal.url import HttpUrl
from .._internal.validated_string import ValidatedString
from .._internal.validator_annotations import (
    Predicate,
    RestrictCharacters,
)
from .._internal.version_type import Version
from .._internal.warning_levels import ALERT, INFO
from ._v0_3_converter import convert_from_older_format
from .v0_2 import Author as _Author_v0_2
from .v0_2 import BadgeDescr, Doi, FileSource_cover, OrcidId, Uploader
from .v0_2 import Maintainer as _Maintainer_v0_2

__all__ = [
    "Author",
    "BadgeDescr",
    "CiteEntry",
    "DeprecatedLicenseId",
    "Doi",
    "FileDescr",
    "GenericDescr",
    "HttpUrl",
    "KNOWN_SPECIFIC_RESOURCE_TYPES",
    "LicenseId",
    "LinkedResource",
    "Maintainer",
    "OrcidId",
    "RelativeFilePath",
    "ResourceId",
    "Sha256",
    "Uploader",
    "VALID_COVER_IMAGE_EXTENSIONS",
    "Version",
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
)


class ResourceId(ValidatedString):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
        Annotated[
            NotEmpty[str],
            RestrictCharacters(string.ascii_lowercase + string.digits + "_-/."),
            annotated_types.Predicate(
                lambda s: not (s.startswith("/") or s.endswith("/"))
            ),
        ]
    ]


def _has_no_slash(s: str) -> bool:
    return "/" not in s and "\\" not in s


class Author(_Author_v0_2):
    name: Annotated[str, Predicate(_has_no_slash)]
    github_user: Optional[str] = None

    @field_validator("github_user", mode="after")
    def _validate_github_user(cls, value: Optional[str]):
        if value is None:
            return None
        else:
            return validate_github_user(value)


class _AuthorConv(Converter[_Author_v0_2, Author]):
    def _convert(
        self, src: _Author_v0_2, tgt: "type[Author] | type[dict[str, Any]]"
    ) -> "Author | dict[str, Any]":
        return tgt(
            name=src.name,
            github_user=src.github_user,
            affiliation=src.affiliation,
            email=src.email,
            orcid=src.orcid,
        )


_author_conv = _AuthorConv(_Author_v0_2, Author)


class Maintainer(_Maintainer_v0_2):
    name: Optional[Annotated[str, Predicate(_has_no_slash)]] = None
    github_user: str

    @field_validator("github_user", mode="after")
    def validate_github_user(cls, value: str):
        return validate_github_user(value)


class _MaintainerConv(Converter[_Maintainer_v0_2, Maintainer]):
    def _convert(
        self, src: _Maintainer_v0_2, tgt: "type[Maintainer | dict[str, Any]]"
    ) -> "Maintainer | dict[str, Any]":
        return tgt(
            name=src.name,
            github_user=src.github_user,
            affiliation=src.affiliation,
            email=src.email,
            orcid=src.orcid,
        )


_maintainer_conv = _MaintainerConv(_Maintainer_v0_2, Maintainer)


class CiteEntry(Node):
    """A citation that should be referenced in work using this resource."""

    text: str
    """free text description"""

    doi: Optional[Doi] = None
    """A digital object identifier (DOI) is the prefered citation reference.
    See https://www.doi.org/ for details.
    Note:
        Either **doi** or **url** have to be specified.
    """

    url: Optional[HttpUrl] = None
    """URL to cite (preferably specify a **doi** instead/also).
    Note:
        Either **doi** or **url** have to be specified.
    """

    @model_validator(mode="after")
    def _check_doi_or_url(self):
        if not self.doi and not self.url:
            raise ValueError("Either 'doi' or 'url' is required")

        return self


class LinkedResourceBase(Node):
    @model_validator(mode="before")
    def _remove_version_number(cls, value: Any):
        if is_dict(value):
            vn = value.pop("version_number", None)
            if vn is not None and value.get("version") is None:
                value["version"] = vn

        return value

    version: Optional[Version] = None
    """The version of the linked resource following SemVer 2.0."""


class LinkedResource(LinkedResourceBase):
    """Reference to a bioimage.io resource"""

    id: ResourceId
    """A valid resource `id` from the official bioimage.io collection."""


class BioimageioConfig(Node, extra="allow"):
    """bioimage.io internal metadata."""


class Config(Node, extra="allow"):
    """A place to store additional metadata (often tool specific).

    Such additional metadata is typically set programmatically by the respective tool
    or by people with specific insights into the tool.
    If you want to store additional metadata that does not match any of the other
    fields, think of a key unlikely to collide with anyone elses use-case/tool and save
    it here.

    Please consider creating [an issue in the bioimageio.spec repository](https://github.com/bioimage-io/spec-bioimage-io/issues/new?template=Blank+issue)
    if you are not sure if an existing field could cover your use case
    or if you think such a field should exist.
    """

    bioimageio: BioimageioConfig = Field(default_factory=BioimageioConfig)
    """bioimage.io internal metadata."""

    @model_validator(mode="after")
    def _validate_extra_fields(self):
        if self.model_extra:
            for k, v in self.model_extra.items():
                if not isinstance(v, Node) and not is_yaml_value(v):
                    raise ValueError(
                        f"config.{k} is not a valid YAML value or `Node` instance"
                    )

        return self

    def __getitem__(self, key: str) -> Any:
        """Allows to access the config as a dictionary."""
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Allows to set the config as a dictionary."""
        setattr(self, key, value)


class GenericModelDescrBase(ResourceDescrBase):
    """Base for all resource descriptions including of model descriptions"""

    name: Annotated[
        Annotated[
            str, RestrictCharacters(string.ascii_letters + string.digits + "_+- ()")
        ],
        MinLen(5),
        MaxLen(128),
        warn(MaxLen(64), "Name longer than 64 characters.", INFO),
    ]
    """A human-friendly name of the resource description.
    May only contains letters, digits, underscore, minus, parentheses and spaces."""

    description: FAIR[
        Annotated[
            str,
            MaxLen(1024),
            warn(MaxLen(512), "Description longer than 512 characters."),
        ]
    ] = ""
    """A string containing a brief description."""

    covers: List[FileSource_cover] = Field(
        default_factory=cast(Callable[[], List[FileSource_cover]], list),
        description=(
            "Cover images. Please use an image smaller than 500KB and an aspect"
            " ratio width to height of 2:1 or 1:1.\nThe supported image formats"
            f" are: {VALID_COVER_IMAGE_EXTENSIONS}"
        ),
        examples=[["cover.png"]],
    )
    """Cover images."""

    id_emoji: Optional[
        Annotated[str, Len(min_length=1, max_length=2), Field(examples=["🦈", "🦥"])]
    ] = None
    """UTF-8 emoji for display alongside the `id`."""

    authors: FAIR[List[Author]] = Field(
        default_factory=cast(Callable[[], List[Author]], list)
    )
    """The authors are the creators of this resource description and the primary points of contact."""

    attachments: List[FileDescr_] = Field(
        default_factory=cast(Callable[[], List[FileDescr_]], list)
    )
    """file attachments"""

    cite: FAIR[List[CiteEntry]] = Field(
        default_factory=cast(Callable[[], List[CiteEntry]], list)
    )
    """citations"""

    license: FAIR[
        Annotated[
            Annotated[
                Union[LicenseId, DeprecatedLicenseId, None],
                Field(union_mode="left_to_right"),
            ],
            warn(
                Optional[LicenseId],
                "{value} is deprecated, see https://spdx.org/licenses/{value}.html",
            ),
            Field(examples=["CC0-1.0", "MIT", "BSD-2-Clause"]),
        ]
    ] = None
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do not support custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
    to discuss your intentions with the community."""

    git_repo: Annotated[
        Optional[HttpUrl],
        Field(
            examples=[
                "https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad"
            ],
        ),
    ] = None
    """A URL to the Git repository where the resource is being developed."""

    icon: Union[Annotated[str, Len(min_length=1, max_length=2)], FileSource_, None] = (
        None
    )
    """An icon for illustration, e.g. on bioimage.io"""

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

    maintainers: List[Maintainer] = Field(
        default_factory=cast(Callable[[], List[Maintainer]], list)
    )
    """Maintainers of this resource.
    If not specified, `authors` are maintainers and at least some of them has to specify their `github_user` name"""

    @model_validator(mode="after")
    def _check_maintainers_exist(self):
        if not self.maintainers and self.authors:
            if all(a.github_user is None for a in self.authors):
                issue_warning(
                    "Missing `maintainers` or any author in `authors` with a specified"
                    + " `github_user` name.",
                    value=self.authors,
                    field="authors",
                    severity=ALERT,
                )

        return self

    tags: FAIR[
        Annotated[
            List[str],
            Field(
                examples=[("unet2d", "pytorch", "nucleus", "segmentation", "dsb2018")]
            ),
        ]
    ] = Field(default_factory=list)
    """Associated tags"""

    @as_warning
    @field_validator("tags")
    @classmethod
    def warn_about_tag_categories(
        cls, value: List[str], info: ValidationInfo
    ) -> List[str]:
        categories = TAG_CATEGORIES.get(info.data["type"], {})
        missing_categories: List[Dict[str, Sequence[str]]] = []
        for cat, entries in categories.items():
            if not any(e in value for e in entries):
                missing_categories.append({cat: entries})

        if missing_categories:
            raise ValueError(
                f"Missing tags from bioimage.io categories: {missing_categories}"
            )

        return value

    version: Optional[Version] = None
    """The version of the resource following SemVer 2.0."""

    @model_validator(mode="before")
    def _remove_version_number(cls, value: Any):
        if is_dict(value):
            vn = value.pop("version_number", None)
            if vn is not None and value.get("version") is None:
                value["version"] = vn

        return value

    version_comment: Optional[Annotated[str, MaxLen(512)]] = None
    """A comment on the version of the resource."""


FileSource_documentation = Annotated[
    FileSource_,
    WithSuffix(".md", case_sensitive=True),
    Field(
        examples=[
            "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md",
            "README.md",
        ],
    ),
]


class GenericDescrBase(GenericModelDescrBase):
    """Base for all resource descriptions except for the model descriptions"""

    implemented_format_version: ClassVar[Literal["0.3.0"]] = "0.3.0"
    if TYPE_CHECKING:
        format_version: Literal["0.3.0"] = "0.3.0"
    else:
        format_version: Literal["0.3.0"]
        """The **format** version of this resource specification"""

    @model_validator(mode="before")
    @classmethod
    def _convert_from_older_format(
        cls, data: BioimageioYamlContent, /
    ) -> BioimageioYamlContent:
        cls.convert_from_old_format_wo_validation(data)
        return data

    @classmethod
    def convert_from_old_format_wo_validation(cls, data: BioimageioYamlContent) -> None:
        """Convert metadata following an older format version to this classes' format
        without validating the result.
        """
        convert_from_older_format(data)

    documentation: FAIR[Optional[FileSource_documentation]] = None
    """URL or relative path to a markdown file encoded in UTF-8 with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory."""

    badges: List[BadgeDescr] = Field(  # pyright: ignore[reportUnknownVariableType]
        default_factory=list
    )
    """badges associated with this resource"""

    config: Config = Field(default_factory=Config.model_construct)
    """A field for custom configuration that can contain any keys not present in the RDF spec.
    This means you should not store, for example, a GitHub repo URL in `config` since there is a `git_repo` field.
    Keys in `config` may be very specific to a tool or consumer software. To avoid conflicting definitions,
    it is recommended to wrap added configuration into a sub-field named with the specific domain or tool name,
    for example:
    ```yaml
    config:
        giraffe_neckometer:  # here is the domain name
            length: 3837283
            address:
                home: zoo
        imagej:              # config specific to ImageJ
            macro_dir: path/to/macro/file
    ```
    If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.
    You may want to list linked files additionally under `attachments` to include them when packaging a resource.
    (Packaging a resource means downloading/copying important linked files and creating a ZIP archive that contains
    an altered rdf.yaml file with local references to the downloaded files.)"""


ResourceDescrType = TypeVar("ResourceDescrType", bound=GenericDescrBase)


class GenericDescr(GenericDescrBase, extra="ignore"):
    """Specification of the fields used in a generic bioimage.io-compliant resource description file (RDF).

    An RDF is a YAML file that describes a resource such as a model, a dataset, or a notebook.
    Note that those resources are described with a type-specific RDF.
    Use this generic resource description, if none of the known specific types matches your resource.
    """

    implemented_type: ClassVar[Literal["generic"]] = "generic"
    if TYPE_CHECKING:
        type: Annotated[str, LowerCase] = "generic"
        """The resource type assigns a broad category to the resource."""
    else:
        type: Annotated[str, LowerCase]
        """The resource type assigns a broad category to the resource."""

    id: Optional[
        Annotated[ResourceId, Field(examples=["affable-shark", "ambitious-sloth"])]
    ] = None
    """bioimage.io-wide unique resource identifier
    assigned by bioimage.io; version **un**specific."""

    parent: Optional[ResourceId] = None
    """The description from which this one is derived"""

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
