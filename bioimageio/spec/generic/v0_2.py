from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Annotated, Any, ClassVar, Dict, Literal, Optional, Tuple, TypeVar, Union, get_args

from annotated_types import Len, MinLen
from pydantic import (
    AnyUrl,
    DirectoryPath,
    EmailStr,
    FieldValidationInfo,
    HttpUrl,
    TypeAdapter,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)

from bioimageio.spec.shared import LICENSES
from bioimageio.spec.shared.common import DOI_REGEX
from bioimageio.spec.shared.fields import Field
from bioimageio.spec.shared.nodes import FrozenDictNode, Node, StringNode
from bioimageio.spec.shared.types import FileSource, LicenseId, RawMapping, RelativeFilePath, Version
from bioimageio.spec.shared.utils import is_valid_orcid_id
from bioimageio.spec.shared.validation import warn  # RAISE_WARNINGS_VALUE, TREAT_WARNINGS_CONTEXT_KEY, as_warning, warn

LatestFormatVersion = Literal["0.2.3"]
FormatVersion = Literal["0.2.0", "0.2.1", "0.2.2", LatestFormatVersion]

LATEST_FORMAT_VERSION: LatestFormatVersion = get_args(LatestFormatVersion)[0]
IN_PACKAGE_MESSAGE = " (included when packaging the resource)"
_VALID_COVER_IMAGE_EXTENSIONS = ["jpg", "png", "gif", "jpeg"]

KnownGenericResourceType = Literal["application", "notebook"]
KnownSpecializedResourceType = Literal["model", "collection", "dataset"]


class Attachments(Node):
    model_config = {**Node.model_config, "extra": "allow"}
    """update pydantic model config to allow additional unknown keys"""
    files: Tuple[FileSource, ...] = Field((), in_package=True)
    """File attachments"""


class Person(Node):
    name: Optional[str] = None
    """Full name"""
    affiliation: Optional[str] = None
    """Affiliation"""
    email: Optional[EmailStr] = None
    """Email"""
    github_user: Optional[str] = None
    """GitHub user name"""
    orcid: Optional[str] = Field(None, examples=["0000-0001-2345-6789"])
    """An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID)
    in hyphenated groups of 4 digits, (and [valid](
    https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
    ) as per ISO 7064 11,2.)
    """

    @field_validator("orcid")
    @classmethod
    def check_orcid(cls, orcid: Optional[str]):
        if orcid is not None and (
            len(orcid) != 19
            or any(orcid[idx] != "-" for idx in [4, 9, 14])
            or not is_valid_orcid_id(orcid.replace("-", ""))
        ):
            raise ValueError(f"'{orcid} is not a valid ORCID iD in hyphenated groups of 4 digits")


class Author(Person):
    name: str = Field(..., description="Full name")


class Maintainer(Person):
    github_user: str = Field(..., description="GitHub user name")


class Badge(Node, title="Custom badge"):
    """A custom badge"""

    label: str = Field(examples=["Open in Colab"])
    """badge label to display on hover"""

    icon: Union[HttpUrl, None] = Field(None, examples=["https://colab.research.google.com/assets/colab-badge.svg"])
    """badge icon"""

    url: HttpUrl = Field(
        examples=[
            "https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb"
        ]
    )
    """target URL"""


class CiteEntry(Node):
    text: str
    """free text description"""

    doi: Optional[str] = Field(None, pattern=DOI_REGEX)
    """A digital object identifier (DOI) is the prefered citation reference.
    See https://www.doi.org/ for details. (alternatively specify `url`)"""

    url: Optional[str] = None
    """URL to cite (preferably specify a `doi` instead)"""

    @field_validator("url", mode="after")
    @classmethod
    def check_doi_or_url(cls, value: Optional[str], info: FieldValidationInfo):
        if not info.data.get("doi") and not value:
            raise ValueError("Either 'doi' or 'url' is required")

        return value


# class ResourceId(StringNode):

#     type: ClassVar[Union[KnownGenericResourceType, KnownSpecializedResourceType, None]] = None


class LinkedResource(Node):
    """Reference to a bioimage.io resource"""

    id: str
    """A valid resource `id` from the bioimage.io collection."""


class ResourceDescriptionBaseNoSource(Node):
    """ResourceDescriptionBase without a source field

    (because `bioimageio.spec.model.v0_5.ModelDescription has no source field)
    """

    format_version: str
    """The format version of this RDF specification
    (not the `version` of the resource described by it)"""

    type: Union[KnownGenericResourceType, str] = Field(examples=list(get_args(KnownGenericResourceType)))
    """The resource type assigns a broad category to the resource
    and determines wether type specific validation, e.g. for `type="model"`, is applicable"""

    name: str
    """A human-friendly name of the resource description"""

    # todo warn about capitalization
    @field_validator("name", mode="after")
    @classmethod
    def check_name(cls, name: str) -> str:
        return name.capitalize()

    description: str
    """A string containing a brief description."""

    documentation: Union[FileSource, None] = Field(
        None,
        examples=[
            "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/README.md",
            "README.md",
        ],
        in_package=True,
    )
    """URL or relative path to a markdown file with additional documentation.
    The recommended documentation file name is `README.md`. An `.md` suffix is mandatory."""

    @field_validator("documentation", mode="after")
    @classmethod
    def check_documentation_suffix(cls, value: Union[FileSource, None]) -> Union[FileSource, None]:
        if value is not None and not str(value).endswith(".md"):
            raise ValueError("Expected markdown file with '.md' suffix")

        return value

    covers: Tuple[FileSource, ...] = Field(
        (),
        examples=[],
        description=(
            "Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. "
            f"The supported image formats are: {_VALID_COVER_IMAGE_EXTENSIONS}"
        ),
        in_package=True,
    )
    """Cover images."""

    @field_validator("covers", mode="after")
    @classmethod
    def check_cover_suffix(cls, value: Sequence[Union[FileSource, None]]) -> Sequence[Union[FileSource, None]]:
        for v in value:
            if (
                v is not None
                and "." not in str(v)
                and str(v).split(".")[-1].lower() not in _VALID_COVER_IMAGE_EXTENSIONS
            ):
                raise ValueError(f"Expected markdown file with suffix in {_VALID_COVER_IMAGE_EXTENSIONS}")

        return value

    id: Optional[str] = None
    """bioimage.io wide, unique identifier assigned by the
    [bioimage.io collection](https://github.com/bioimage-io/collection-bioimage-io)"""

    authors: Tuple[Author, ...] = ()
    """The authors are the creators of the RDF and the primary points of contact."""

    attachments: Optional[Attachments] = None
    """file and other attachments"""

    badges: Tuple[Badge, ...] = ()
    """badges associated with this resource"""

    cite: Annotated[Tuple[CiteEntry, ...], warn(Annotated[Tuple[CiteEntry, ...], MinLen(1)])] = ()
    """citations"""

    config: Optional[FrozenDictNode] = Field(
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

    download_url: Union[HttpUrl, None] = None
    """optional URL to download the resource from (deprecated)"""

    git_repo: Optional[str] = Field(
        None,
        examples=["https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_specs/models/unet2d_nuclei_broad"],
    )
    """A URL to the Git repository where the resource is being developed."""

    icon: Union[FileSource, Annotated[str, Len(min_length=1, max_length=2)], None] = None
    """an icon for illustration"""

    # todo: make license mandatory
    license: Union[LicenseId, str, None] = Field(None, examples=["MIT", "CC-BY-4.0", "BSD-2-Clause"])
    """A [SPDX license identifier](https://spdx.org/licenses/).
    We do not support custom license beyond the SPDX license list, if you need that please
    [open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
    to discuss your intentions with the community."""

    # @as_warning
    # @field_validator("license", mode="after")
    # @classmethod
    # def deprecated_spdx_license(cls, value: Optional[str], info: ValidationInfo):
    #     if value is None or info.context.get(TREAT_WARNINGS_CONTEXT_KEY) != RAISE_WARNINGS_VALUE:
    #         return value

    #     if value not in LICENSES:
    #         raise ValueError(f"{value} is not a recognized SPDX license identifier. See https://spdx.org/licenses/")

    #     license_info = LICENSES[value]
    #     if license_info.get("isDeprecatedLicenseId", False):
    #         raise ValueError(f"{value} ({license_info['name']}) is deprecated.")

    #     # if not license_info.get("isFsfLibre", False):
    #     #     self.warn("license", f"{value} ({license_info['name']}) is not FSF Free/libre.")

    #     return value

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

    maintainers: Tuple[Maintainer, ...] = ()
    """Maintainers of this resource.
    If not specified `authors` are maintainers and at least some of them should specify their `github_user` name"""

    rdf_source: Union[HttpUrl, None] = None
    """resource description file (RDF) source; used to keep track of where an rdf.yaml was downloaded from"""

    root: Union[DirectoryPath, AnyUrl]
    """Base path or URL for any relative paths specified in the RDF"""

    tags: Tuple[str, ...] = Field((), examples=[("unet2d", "pytorch", "nucleus", "segmentation", "dsb2018")])
    """"Associated tags"""

    # todo warn about tags
    # @field_validator("tags")
    # def warn_about_tag_categories(self, value):
    #     missing_categories = []
    #     try:
    #         categories = {
    #             c["type"]: c.get("tag_categories", {}) for c in BIOIMAGEIO_SITE_CONFIG["resource_categories"]
    #         }.get(self.__class__.__name__.lower(), {})
    #         for cat, entries in categories.items():
    #             if not any(e in value for e in entries):
    #                 missing_categories.append({cat: entries})
    #     except Exception as e:
    #         error = str(e)
    #     else:
    #         error = None
    #         if missing_categories:
    #             self.warn("tags", f"Missing tags corresponding to bioimage.io categories: {missing_categories}")

    #     if error is not None:
    #         self.warn("tags", f"could not check tag categories ({error})")

    version: Union[Version, None] = Field(None, examples=["0.1.0"])
    """The version number of the resource. Its format must be a string in
    `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/).
    Hyphens and plus signs are not allowed to be compatible with
    https://packaging.pypa.io/en/stable/version.html.
    The initial version should be `"0.1.0"`."""

    def __init__(self, *, _context: Optional[dict[str, Any]] = None, **data: Any) -> None:
        # set 'root' context from 'root' kwarg when constructing an RescourceDescription
        given_root = self._validate_root(data.get("root"), raise_=False, allow_none=True)
        context = _context or {}
        if given_root is not None:
            context["root"] = given_root

        self.__pydantic_validator__.validate_python(data, self_instance=self, context=context)

    @classmethod
    def _validate_root(cls, value: Any, *, raise_: bool, allow_none: bool):
        if allow_none and value is None:
            return None

        root_validator = TypeAdapter(cls.model_fields["root"].annotation)
        try:
            root = root_validator.validate_python(value)
        except ValidationError:
            root = value
            if raise_:
                raise
        else:
            if isinstance(root, Path):
                root = root.resolve()

        return root

    @classmethod
    def convert_from_older_format(cls, data: RawMapping) -> RawMapping:
        """convert raw RDF data of an older format where possible"""
        # check if we have future format version
        fv = data.get("format_version", "0.2.0")
        if isinstance(fv, str) and tuple(map(int, fv.split(".")[:2])) >= (0, 3):
            return data

        data = dict(data)

        # we unofficially accept strings as author entries
        authors = data.get("authors")
        if isinstance(authors, list):
            data["authors"] = [{"name": a} if isinstance(a, str) else a for a in authors]  # type: ignore

        if data.get("format_version") in ("0.2.0", "0.2.1"):
            data["format_version"] = "0.2.2"

        if data.get("format_version") == "0.2.2":
            cls._remove_slashes_from_names(data)
            data["format_version"] = "0.2.3"

        return data

    @staticmethod
    def _remove_slashes_from_names(data: dict[str, Any]) -> None:
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

    @classmethod
    def model_validate(
        cls: type[ResourceDescriptionType],
        obj: dict[str, Any],
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> ResourceDescriptionType:
        """Validate RDF content `obj` and create an RDF instance.

        Also sets 'root' context from 'root' in `obj` (or vice versa)

        Args:
            cls: The model class to use.
            obj: The object to validate.
            strict: Whether to raise an exception on invalid fields. Defaults to None.
            from_attributes: Whether to extract data from object attributes. Defaults to None.
            context: Additional context to pass to the validator. Defaults to None.

        Raises:
            ValidationError: If the object could not be validated.

        Returns:
            The validated RDF instance.

        """
        assert isinstance(obj, dict)
        if from_attributes:
            raise NotImplementedError("from_attributes")

        given_root = cls._validate_root(obj.get("root"), raise_=False, allow_none=True)
        context_root = cls._validate_root((context or {}).get("root"), raise_=True, allow_none=True)

        if given_root and context_root and (given_root != context_root):
            raise ValueError(
                f"'root' specified as field and as context and they disagree: {given_root} != {context_root}."
            )

        if given_root and not context_root:
            context = {**(context or {}), "root": given_root}
        elif context_root and not given_root:
            obj = dict(obj)
            obj["root"] = context_root

        data = cls.convert_from_older_format(obj)
        return super().model_validate(data, strict=strict, from_attributes=from_attributes, context=context)

    @field_validator("type", mode="before")
    @classmethod
    def set_type_default(cls, value: Optional[str]) -> str:
        if value is None:
            return cls.__name__.lower()
        else:
            return value


ResourceDescriptionType = TypeVar("ResourceDescriptionType", bound=ResourceDescriptionBaseNoSource)


class ResourceDescriptionBase(ResourceDescriptionBaseNoSource):
    model_config = {**ResourceDescriptionBaseNoSource.model_config, "extra": "ignore"}
    source: Union[FileSource, None] = Field(None, description="URL or relative path to the source of the resource")
    """The primary source of the resource"""

    def __init__(self, *, _context: Union[dict[str, Any], None] = None, **data: Any) -> None:
        super().__init__(_context=_context, **data)


class GenericDescription(ResourceDescriptionBase):
    """Specification of the fields used in a generic bioimage.io-compliant resource description file (RDF).

    An RDF is a YAML file that describes a resource such as a model, a dataset, an application or a notebook.
    Note that models are described with an extended model RDF specification.
    """

    model_config = {
        **ResourceDescriptionBase.model_config,
        **dict(title=f"bioimage.io generic RDF {get_args(FormatVersion)[-1]}"),
    }
    """pydantic model_config"""

    format_version: LatestFormatVersion = LATEST_FORMAT_VERSION

    @field_validator("type", mode="after")
    @classmethod
    def check_specific_types(cls, value: str) -> str:
        if value in get_args(KnownSpecializedResourceType):
            raise ValueError(
                f"Use the {value} description instead of the generic description for resources of type {value}."
            )

        return value
