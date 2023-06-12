from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Any, ClassVar, Literal, Optional, TypeVar, Union, get_args

import annotated_types
import packaging.version
import pydantic
from pydantic import (
    AnyUrl,
    DirectoryPath,
    EmailStr,
    Extra,
    HttpUrl,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)

from bioimageio.spec.shared.common import DOI_REGEX
from bioimageio.spec.shared.fields import Field, RelativePath
from bioimageio.spec.shared.nodes import Node
from bioimageio.spec.shared.types_ import RawMapping
from bioimageio.spec.shared.utils import is_valid_orcid_id


LatestFormatVersion = Literal["0.2.3"]
FormatVersion = Literal["0.2.0", "0.2.1", "0.2.2", LatestFormatVersion]

LATEST_FORMAT_VERSION: LatestFormatVersion = get_args(LatestFormatVersion)[0]


class Attachments(Node):
    model_config = Node.model_config | dict(extra=Extra.allow)
    files: Optional[tuple[Union[HttpUrl, RelativePath], ...]] = Field(
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


class RdfBase(Node):
    bioimageio_description: ClassVar[str]
    format_version: str
    type: str = Field(None, description="Type of the resource")
    name: str = Field(..., description="a human-friendly name of the resource")
    # description: str = Field(description=)

    attachments: Union[Attachments, None] = Field(None, description="Attachments; additional unknown keys are allowed")
    authors: Annotated[
        tuple[Author],
        annotated_types.Len(min_length=1),
    ] = Field(
        description=(
            "A list of authors. The authors are the creators of the specifications and the primary points of contact."
        )
    )

    # badges: Union[_Missing, List[Badge]] = Field(None, description=)
    # cite: Union[_Missing, List[CiteEntry]] = Field(None, description=)
    # config: Union[_Missing, dict] = Field(None, description=)
    # covers: Union[_Missing, List[Union[URI, Path]]] = Field(None, description=)
    # documentation: Union[_Missing, Path, URI] = Field(None, description=)
    # download_url: Union[_Missing, Path, URI] = Field(None, description=)
    # git_repo: Union[_Missing, str] = Field(None, description=)
    # icon: Union[_Missing, str] = Field(None, description=)
    # id: Union[_Missing, str] = Field(None, description=)
    # license: Union[_Missing, str] = Field(None, description=)
    # links: Union[_Missing, List[str]] = Field(None, description=)
    # maintainers: Union[_Missing, List[Maintainer]] = Field(None, description=)
    # rdf_source: Union[_Missing, URI] = Field(None, description=)
    root: Union[DirectoryPath, AnyUrl] = pydantic.Field(description="Base for any relative paths specified in the RDF")
    # source: Union[_Missing, URI, Path] = Field(None, description=)
    # tags: Union[_Missing, List[str]] = Field(None, description=)
    version: Union[str, None] = Field(
        None,
        description="The version number of the resource. Its format must be a string in "
        "`MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/). "
        "Hyphens and plus signs are not allowed to be compatible with "
        "https://packaging.pypa.io/en/stable/version.html. "
        "The initial version number should be `0.1.0`.",
    )

    def __init__(self, **data: Any) -> None:
        # set 'root' context from 'root' kwarg when constructing an Rdf
        given_root = self._validate_root(data.get("root"), raise_=False, allow_none=True)
        self.__pydantic_validator__.validate_python(data, self_instance=self, context=dict(root=given_root))  # type: ignore

    @classmethod
    def _validate_root(cls, value: Any, *, raise_: bool, allow_none: bool):
        if allow_none and value is None:
            return None

        root_validator = TypeAdapter(RdfBase.model_fields["root"].annotation)
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
    def model_validate(
        cls: type[RdfNodeType],
        obj: dict[str, Any],
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> RdfNodeType:
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
        if from_attributes:
            raise NotImplementedError("from_attributes")

        given_root = cls._validate_root(obj.get("root"), raise_=False, allow_none=True)
        context_root = cls._validate_root((context or {}).get("root"), raise_=True, allow_none=True)

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

    @field_validator("version", mode="after")
    @classmethod
    def check_version(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        if not re.fullmatch(r"^\s*" + packaging.version.VERSION_PATTERN + r"\s*$", value, re.VERBOSE | re.IGNORECASE):
            raise ValueError(
                f"'{value}' is not a valid version string, "
                "see https://packaging.pypa.io/en/stable/version.html for help"
            )


RdfNodeType = TypeVar("RdfNodeType", bound=RdfBase)


class Rdf(RdfBase):
    model_config = RdfBase.model_config | dict(extra=Extra.ignore)
    bioimageio_description = f"""# BioImage.IO Resource Description File Specification {get_args(FormatVersion)[-1]}
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks.
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be
specified.
"""
    format_version: LatestFormatVersion = LATEST_FORMAT_VERSION
