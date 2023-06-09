"""nodes for the general RDF spec

nodes represent the content of any RDF.
"""
# from __future__ import annotations
import pathlib

import packaging.version
import warnings
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union, Annotated, get_args

from pydantic import (
    EmailStr,
    Extra,
    FilePath,
    HttpUrl,
    ValidationError,
    constr,
    field_validator,
    validator,
    DirectoryPath,
    VERSION as PYDANTIC_VERSION,
)

from bioimageio.spec.shared.fields import RelativePath, Version, Field

from bioimageio.spec.shared.nodes import Node

from typing import Literal

from bioimageio.spec.shared.types_ import RawMapping
from bioimageio.spec.shared.utils import is_valid_orcid_id


FormatVersion = Literal[
    "0.2.0", "0.2.1", "0.2.2", "0.2.3"
]  # newest format needs to be last (used to determine latest format version)


class Attachments(Node):
    model_config = Node.model_config | dict(extra=Extra.allow)
    files: Union[Tuple[Union[HttpUrl, RelativePath], ...], None] = Field(
        description="File attachments; included when packaging the resource.", in_package=True
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

    @validator("orcid")
    def check_orcid(cls, orcid: str):
        if (
            len(orcid) != 19
            or any(orcid[idx] != "-" for idx in [4, 9, 14])
            or not is_valid_orcid_id(orcid.replace("-", ""))
        ):
            raise ValueError(f"'{orcid} is not a valid ORCID iD in hyphenated groups of 4 digits")


class Author(_Person):
    name: str = Field(..., description="Full name")


class Maintainer(_Person):
    github_user: str = Field(..., description="GitHub user name")


class CiteEntry(Node):
    text: str
    doi: Optional[str] = None
    url: Optional[str] = None

    @validator("url", always=True)
    def check_doi_or_url(cls, url: Optional[str], values: RawMapping):
        if not values.get("doi") and not url:
            raise ValueError("Either 'doi' or 'url' is required")
        return url


class Badge(Node, title="Custom badge"):
    label: str = Field(..., description="e.g. 'Open in Colab'")
    icon: Optional[HttpUrl] = Field(None, description="e.g. 'https://colab.research.google.com/assets/colab-badge.svg'")
    url: HttpUrl = Field(
        ...,
        description="e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'",
    )


class RDF_Base(Node):
    format_version: Version
    name: str = Field(..., description="a human-friendly name of the resource")
    type: str = Field(None, description="Type of the resource")

    # @validator("type", pre=True)
    @field_validator("type", mode="before")
    @classmethod
    def set_type_default(cls, value: Optional[Any]):
        if value is None:
            return cls.__name__.lower()


#     version: Optional[packaging.version.Version] = Field(
#         None,
#         description="The version number of the resource. Its format must be a string in "
#         "`MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/). "
#         "The initial version number should be `0.1.0`.",
#     )
#     root_path: Union[HttpUrl, DirectoryPath] = Field(
#         pathlib.Path(), description="Base for any relative paths specified in the RDF"
#     )
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


# class RDF(RDF_Base):
#     format_version: Version = Field(get_args(FormatVersion)[-1], const=get_args(FormatVersion)[-1])
