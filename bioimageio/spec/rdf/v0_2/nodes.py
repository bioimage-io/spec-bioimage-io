"""nodes defining the general RDF spec"""
from __future__ import annotations
from typing import Annotated, Any, Optional, Tuple, Type, TypeVar, Union

from pydantic import (
    AnyUrl,
    DirectoryPath,
    EmailStr,
    Extra,
    HttpUrl,
    TypeAdapter,
    field_validator,
    model_validator,
    validator,
)
import pydantic
from pydantic_core import core_schema
from bioimageio.spec.shared.common import DOI_REGEX

from bioimageio.spec.shared.fields import RelativePath, Version, Field

from bioimageio.spec.shared.nodes import Node

from typing import Literal

from bioimageio.spec.shared.types_ import RawMapping
from bioimageio.spec.shared.utils import is_valid_orcid_id


FormatVersion = Literal[
    "0.2.0", "0.2.1", "0.2.2", "0.2.3"
]  # newest format needs to be last (used to determine latest format version)


class RdfBase(Node):
    format_version: Version
    type: str = Field(None, description="Type of the resource")
    name: str = Field(..., description="a human-friendly name of the resource")

    root: Union[AnyUrl, DirectoryPath] = pydantic.Field(description="Base for any relative paths specified in the RDF")
    version: Optional[Version] = Field(
        None,
        description="The version number of the resource. Its format must be a string in "
        "`MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/). "
        "Hyphens and plus signs are not allowed to be compatible with https://packaging.pypa.io/en/stable/version.html. "
        "The initial version number should be `0.1.0`.",
    )

    def __init__(self, **data: Any) -> None:
        """set 'root' context from 'root' kwarg when constructing an Rdf"""
        self.__pydantic_validator__.validate_python(data, self_instance=self, context=dict(root=data.get("root")))  # type: ignore

    @classmethod
    def model_validate(
        cls: type[RdfNodeType],
        obj: RawMapping,
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> RdfNodeType:
        """set 'root' context from 'root' in `obj` (or vice versa) when using 'Rdf.model_validate()'"""
        if from_attributes:
            raise NotImplementedError("from_attributes")

        given_root = obj.get("root")
        context_root = (context or {}).get("root")
        if given_root and context_root and (given_root != context_root):
            raise ValueError(
                f"'root' specified as field and as context and they disagree: {given_root} != {context_root}."
            )

        if given_root and not context_root:
            context = (context or {}) | dict(root=given_root)
        elif context_root and not given_root:
            obj = dict(obj) | dict(root=context_root)

        return super().model_validate(obj, strict=strict, from_attributes=from_attributes, context=context)

    @field_validator("type", mode="before")
    @classmethod
    def set_type_default(cls, value: Optional[str]) -> str:
        if value is None:
            return cls.__name__.lower()
        else:
            return value

    # @field_validator("_root", mode="before")
    # @classmethod
    # def set_root(cls, value: Any, info: core_schema.ValidationInfo) -> str:
    #     return info.context.get("root")

    # # @model_validator(mode='before')
    # @field_validator("root", mode="before")
    # def set_root_from_context(cls, data: RawMapping, info: core_schema.ValidationInfo):
    #     # root_validator = TypeAdapter(Union[AnyUrl, DirectoryPath, None])
    #     root_in_context = root_validator.validate_python((info.context or {}).get("root"))
    #     root_in_data = root_validator.validate_python(data.get("root"))

    #     if root_in_context is None and root_in_data is None:
    #         raise ValueError("")
    #     info.context = data.get("root")

    #     return data


#     # attachments: Union[_Missing, Attachments] = missing
#     # authors: Union[_Missing, List[Author]] = missing
#     # badges: Union[_Missing, List[Badge]] = missing
#     # cite: Union[_Missing, List[CiteEntry]] = missing
#     # config: Union[_Missing, dict] = missing
#     # covers: Union[_Missing, List[Union[URI, Path]]] = missing
#     # description: str = missing
#     # documentation: Union[_Missing, Path, URI] = missing
#     # download_url: Union[_Missing, Path, URI] = missing
#     # git_repo: Union[_Missing, str] = missing
#     # id: Union[_Missing, str] = missing
#     # icon: Union[_Missing, str] = missing
#     # license: Union[_Missing, str] = missing
#     # links: Union[_Missing, List[str]] = missing
#     # maintainers: Union[_Missing, List[Maintainer]] = missing
#     # rdf_source: Union[_Missing, URI] = missing
#     # source: Union[_Missing, URI, Path] = missing
#     # tags: Union[_Missing, List[str]] = missing


# #     def __post_init__(self):
# #         if self.type is missing:
# #             self.type = self.__class__.__name__.lower()

# #         super().__post_init__()

RdfNodeType = TypeVar("RdfNodeType", bound=RdfBase)

# class RDF(RDF_Base):
#     format_version: Version = Field(get_args(FormatVersion)[-1], const=get_args(FormatVersion)[-1])


class Attachments(Node):
    model_config = Node.model_config | dict(extra=Extra.allow)
    files: Optional[Tuple[Union[HttpUrl, RelativePath], ...]] = Field(
        None, description="File attachments; included when packaging the resource.", in_package=True
    )


class _Person(Node):
    name: Optional[str] = Field(None, description="Full name")
    affiliation: Optional[str] = Field(None, description="Affiliation")
    email: Optional[EmailStr] = Field(None, description="Email")
    github_user: Optional[str] = Field(None, description="GitHub user name")
    orcid: Optional[str] = Field(
        None,
        description=(
            "An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID)"
            "in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid]("
            "https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier"
            ") as per ISO 7064 11,2.)"
        ),
    )

    @field_validator("orcid")
    def check_orcid(cls, orcid: Optional[str]):
        if orcid is not None and (
            len(orcid) != 19
            or any(orcid[idx] != "-" for idx in [4, 9, 14])
            or not is_valid_orcid_id(orcid.replace("-", ""))
        ):
            raise ValueError(f"'{orcid} is not a valid ORCID iD in hyphenated groups of 4 digits")


class Author(_Person):
    name: str = Field(..., description="Full name")


class Maintainer(_Person):
    github_user: str = Field(..., description="GitHub user name")


class Badge(Node, title="Custom badge"):
    label: str = Field(..., description="e.g. 'Open in Colab'")
    icon: Optional[HttpUrl] = Field(None, description="e.g. 'https://colab.research.google.com/assets/colab-badge.svg'")
    url: HttpUrl = Field(
        ...,
        description="e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'",
    )


class CiteEntry(Node):
    text: str
    doi: Optional[str] = Field(None, pattern=DOI_REGEX)
    url: Optional[str] = None

    @model_validator(mode="before")
    def check_doi_or_url(cls, data: RawMapping):
        if not data.get("doi") and not data.get("url"):
            raise ValueError("Either 'doi' or 'url' is required")

        return data
