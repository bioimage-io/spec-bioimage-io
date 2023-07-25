from collections.abc import Mapping, Sequence
from typing import Any, Dict, List, Literal, Optional, Tuple, TypeVar, Union, get_args

from annotated_types import Len, LowerCase, MaxLen
from pydantic import (
    AnyUrl,
    ConfigDict,
    DirectoryPath,
    FieldValidationInfo,
    field_validator,
)
from typing_extensions import Annotated

from bioimageio.spec._internal._constants import LICENSES, TAG_CATEGORIES
from bioimageio.spec._internal._utils import Field
from bioimageio.spec._internal._validate import WithSuffix
from bioimageio.spec._internal._warn import WARNING, as_warning, warn
from bioimageio.spec.generic import v0_2
from bioimageio.spec.shared.nodes import FrozenDictNode, Node
from bioimageio.spec.shared.types import (
    DeprecatedLicenseId,
    FileSource,
    LicenseId,
    NonEmpty,
    RawDict,
    Sha256,
    Version,
)

SpecificResourceType = Literal["application", "collection", "dataset", "model", "notebook"]


class Attachment(Node):
    source: FileSource = Field(in_package=True)
    sha256: Annotated[Optional[Sha256], warn(Sha256)] = None


class LinkedResource(Node):
    """Reference to a bioimage.io resource"""

    id: NonEmpty[str]
    """A valid resource `id` from the official bioimage.io collection."""


class GenericBaseNoSource(Node, metaclass=v0_2.GenericBaseNoSourceMeta):
    """GenericBaseNoFormatVersion without a source field

    (because `bioimageio.spec.model.v0_5.ModelDescription has no source field)
    """

    format_version: str
    """The format version of this resource specification
    (not the `version` of the resource description)"""

    name: Annotated[str, MaxLen(128)]
    """A human-friendly name of the resource description"""

    # todo warn about capitalization
    @field_validator("name", mode="after")
    @classmethod
    def check_name(cls, name: str) -> str:
        return name.capitalize()

    description: Annotated[str, MaxLen(512), warn(MaxLen(256))]
    """A string containing a brief description."""

    documentation: Union[Annotated[FileSource, WithSuffix(".md", case_sensitive=True)], None] = Field(
        None,
        examples=[
            "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/README.md",
            "README.md",
        ],
        in_package=True,
    )
    """URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory."""

    covers: Tuple[
        Annotated[FileSource, WithSuffix(v0_2.VALID_COVER_IMAGE_EXTENSIONS, case_sensitive=False)], ...
    ] = Field(
        (),
        examples=[],
        description=(
            "Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. "
            f"The supported image formats are: {v0_2.VALID_COVER_IMAGE_EXTENSIONS}"
        ),
        in_package=True,
    )
    """Cover images."""

    id: Optional[str] = None
    """bioimage.io wide, unique identifier assigned by the
    [bioimage.io collection](https://github.com/bioimage-io/collection-bioimage-io)"""

    authors: NonEmpty[Tuple[v0_2.Author, ...]]
    """The authors are the creators of the RDF and the primary points of contact."""

    attachments: Tuple[Attachment, ...] = ()
    """file and other attachments"""

    badges: Tuple[v0_2.Badge, ...] = ()
    """badges associated with this resource"""

    cite: NonEmpty[Tuple[v0_2.CiteEntry, ...]]
    """citations"""

    config: Optional[FrozenDictNode[str, Any]] = Field(
        None,
        examples=[
            dict(
                bioimage_io={"my_custom_key": 3837283, "another_key": {"nested": "value"}},
                imagej={"macro_dir": "path/to/macro/file"},
            )
        ],
    )
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

    git_repo: Optional[str] = Field(
        None,
        examples=["https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_specs/models/unet2d_nuclei_broad"],
    )
    """A URL to the Git repository where the resource is being developed."""

    icon: Union[FileSource, Annotated[str, Len(min_length=1, max_length=2)], None] = None
    """an icon for illustration"""

    license: Annotated[
        Union[LicenseId, DeprecatedLicenseId],
        warn(LicenseId, WARNING, "'{value}' is a deprecated or unknown license identifier."),
    ] = Field(examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"])
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do not support custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
    to discuss your intentions with the community."""

    @as_warning
    @field_validator("license", mode="after")
    @classmethod
    def deprecated_spdx_license(cls, value: Optional[str]):
        license_info = LICENSES[value] if value in LICENSES else {}
        if not license_info.get("isFsfLibre", False):
            raise ValueError(f"{value} ({license_info['name']}) is not FSF Free/libre.")

        return value

    links: Tuple[str, ...] = Field(
        (),
        examples=[
            (
                "ilastik/ilastik",
                "deepimagej/deepimagej",
                "zero/notebook_u-net_3d_zerocostdl4mic",
            )
        ],
    )
    """IDs of other bioimage.io resources"""

    maintainers: Tuple[v0_2.Maintainer, ...] = ()
    """Maintainers of this resource.
    If not specified, `authors` are maintainers and at least some of them has to specify their `github_user` name"""

    @field_validator("maintainers", mode="after")
    @classmethod
    def check_maintainers_exist(
        cls, maintainers: Tuple[v0_2.Maintainer, ...], info: FieldValidationInfo
    ) -> Tuple[v0_2.Maintainer, ...]:
        if not maintainers and "authors" in info.data:
            authors: Tuple[v0_2.Author, ...] = info.data["authors"]
            if all(a.github_user is None for a in authors):
                raise ValueError(
                    "Missing `maintainers` or any author in `authors` with a specified `github_user` name."
                )

        return maintainers

    rdf_source: Optional[FileSource] = None
    """resource description file (RDF) source; used to keep track of where an rdf.yaml was downloaded from"""

    root: Union[DirectoryPath, AnyUrl] = DirectoryPath()
    """Base path or URL for any relative paths specified in the RDF"""

    tags: Tuple[str, ...] = Field((), examples=[("unet2d", "pytorch", "nucleus", "segmentation", "dsb2018")])
    """"Associated tags"""

    @as_warning
    @field_validator("tags")
    @classmethod
    def warn_about_tag_categories(cls, value: Tuple[str, ...], info: FieldValidationInfo):
        categories = TAG_CATEGORIES.get(info.data["type"], {})
        missing_categories: List[Mapping[str, Sequence[str]]] = []
        for cat, entries in categories.items():
            if not any(e in value for e in entries):
                missing_categories.append({cat: entries})

        if missing_categories:
            raise ValueError("Missing tags from bioimage.io categories: {missing_categories}")

    version: Union[Version, None] = Field(None, examples=["0.1.0"])
    """The version number of the resource. Its format must be a string in
    `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/).
    Hyphens and plus signs are not allowed to be compatible with
    https://packaging.pypa.io/en/stable/version.html.
    The initial version should be `"0.1.0"`."""

    @classmethod
    def convert_from_older_format(cls, data: RawDict) -> None:
        """convert raw RDF data of an older format where possible"""
        # check if we have future format version
        v0_2.GenericBaseNoSource.convert_from_older_format(data)

        data.pop("download_url", None)

        data["format_version"] = "0.3.0"

    @staticmethod
    def _remove_slashes_from_names(data: Dict[str, Any]) -> None:
        """edit `data` shallowly to remove slashes from names"""
        NAME = "name"
        if NAME in data and isinstance(data[NAME], str):
            data[NAME] = data[NAME].replace("/", "").replace("\\", "")

        # update authors and maintainers
        def rm_slashes_in_person_name(person: Union[Any, Mapping[Union[Any, str], Any]]) -> Any:
            if not isinstance(person, Mapping):
                return person

            new_person = dict(person)  # don't overwrite input data in depth
            if isinstance(n := person.get(NAME), str):
                new_person[NAME] = n.replace("/", "").replace("\\", "")

            return new_person

        for group in ("authors", "maintainers"):
            persons = data.get(group)
            if isinstance(persons, Sequence):
                data[group] = [rm_slashes_in_person_name(p) for p in persons]  # type: ignore


ResourceDescriptionType = TypeVar("ResourceDescriptionType", bound=GenericBaseNoSource)


class GenericBaseNoFormatVersion(GenericBaseNoSource):
    """GenericBase without a format version"""

    source: Union[FileSource, None] = Field(None, description="URL or relative path to the source of the resource")
    """The primary source of the resource"""


class GenericBase(GenericBaseNoFormatVersion):
    model_config = {**GenericBaseNoFormatVersion.model_config, "extra": "ignore"}
    """pydantic model config"""

    format_version: Literal["0.3.0"] = "0.3.0"


class Generic(GenericBase):
    """Specification of the fields used in a generic bioimage.io-compliant resource description file (RDF).

    An RDF is a YAML file that describes a resource such as a model, a dataset, or a notebook.
    Note that those resources are described with a type-specific RDF.
    Use this generic resource description, if none of the known specific types matches your resource.
    """

    model_config = ConfigDict(
        {
            **GenericBase.model_config,
            **ConfigDict(title="bioimage.io generic specification"),
        }
    )
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


AnyGeneric = Annotated[Union[v0_2.Generic, Generic], Field(discriminator="format_version")]
