"""nodes for the general RDF spec

nodes represent the content of any RDF.
"""
import dataclasses
import pathlib

import packaging.version
import warnings
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union, Annotated

from pydantic import EmailStr, Extra, Field, FilePath, HttpUrl, ValidationError, constr, validator
from bioimageio.spec.shared.nodes import Node

from typing import Literal

from bioimageio.spec.shared.types_ import RawMapping
from bioimageio.spec.shared.utils import is_valid_orcid_id

FormatVersion = Literal[
    "0.2.0", "0.2.1", "0.2.2", "0.2.3"
]  # newest format needs to be last (used to determine latest format version)


class Attachments(Node, extra=Extra.allow):
    files: Union[Tuple[Union[HttpUrl, PurePosixPath], ...], None] = Field(
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


class Badge(Node):
    label: str
    icon: Union[HttpUrl, Annotated[str, constr(min_length=1, max_length=2), PurePosixPath], None] = None
    url: HttpUrl


# @dataclass
# class RDF_Base(ResourceDescription):
#     attachments: Union[_Missing, Attachments] = missing
#     authors: Union[_Missing, List[Author]] = missing
#     badges: Union[_Missing, List[Badge]] = missing
#     cite: Union[_Missing, List[CiteEntry]] = missing
#     config: Union[_Missing, dict] = missing
#     covers: Union[_Missing, List[Union[URI, Path]]] = missing
#     description: str = missing
#     documentation: Union[_Missing, Path, URI] = missing
#     download_url: Union[_Missing, Path, URI] = missing
#     format_version: str = missing
#     git_repo: Union[_Missing, str] = missing
#     id: Union[_Missing, str] = missing
#     icon: Union[_Missing, str] = missing
#     license: Union[_Missing, str] = missing
#     links: Union[_Missing, List[str]] = missing
#     maintainers: Union[_Missing, List[Maintainer]] = missing
#     rdf_source: Union[_Missing, URI] = missing
#     source: Union[_Missing, URI, Path] = missing
#     tags: Union[_Missing, List[str]] = missing

#     # manual __init__ to allow for unknown kwargs
#     def __init__(
#         self,
#         *,
#         # ResourceDescription
#         format_version: str,
#         name: str,
#         type: str = missing,
#         version: Union[_Missing, packaging.version.Version] = missing,
#         root_path: pathlib.Path = pathlib.Path(),
#         # RDF
#         attachments: Union[_Missing, Dict[str, Any]] = missing,
#         authors: Union[_Missing, List[Author]] = missing,
#         badges: Union[_Missing, List[Badge]] = missing,
#         cite: Union[_Missing, List[CiteEntry]] = missing,
#         config: Union[_Missing, dict] = missing,
#         covers: Union[_Missing, List[Union[URI, Path]]] = missing,
#         description: str,
#         documentation: Union[_Missing, Path, URI] = missing,
#         download_url: Union[_Missing, Path, URI] = missing,
#         git_repo: Union[_Missing, str] = missing,
#         id: Union[_Missing, str] = missing,
#         icon: Union[_Missing, str] = missing,
#         license: Union[_Missing, str] = missing,
#         links: Union[_Missing, List[str]] = missing,
#         maintainers: Union[_Missing, List[Maintainer]] = missing,
#         rdf_source: Union[_Missing, URI] = missing,
#         source: Union[_Missing, URI, Path] = missing,
#         tags: Union[_Missing, List[str]] = missing,
#         **unknown_kwargs,
#     ):
#         self.attachments = attachments
#         self.authors = authors
#         self.badges = badges
#         self.cite = cite
#         self.config = config
#         self.covers = covers
#         self.description = description
#         self.documentation = documentation
#         self.download_url = download_url
#         self.git_repo = git_repo
#         self.id = id
#         self.icon = icon
#         self.license = license
#         self.links = links
#         self.maintainers = maintainers
#         self.rdf_source = rdf_source
#         self.source = source
#         self.tags = tags
#         super().__init__(format_version=format_version, name=name, type=type, version=version, root_path=root_path)

#         if unknown_kwargs:
#             # make sure we didn't forget a defined field
#             field_names = set(f.name for f in dataclasses.fields(self))
#             for uk in unknown_kwargs:
#                 assert uk not in field_names, uk

#             warnings.warn(f"discarding unknown RDF fields: {unknown_kwargs}")

#     def __post_init__(self):
#         if self.type is missing:
#             self.type = self.__class__.__name__.lower()

#         super().__post_init__()


# @dataclass(init=False)
# class RDF(RDF_Base):
#     format_version: FormatVersion = missing
