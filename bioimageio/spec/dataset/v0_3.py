from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, cast

from pydantic import model_validator

from .._internal.common_nodes import InvalidDescr, Node
from .._internal.io import FileDescr as FileDescr
from .._internal.io import Sha256 as Sha256
from .._internal.io_basics import AbsoluteFilePath as AbsoluteFilePath
from .._internal.types import DatasetId as DatasetId
from .._internal.url import HttpUrl as HttpUrl
from ..generic.v0_3 import Author as Author
from ..generic.v0_3 import BadgeDescr as BadgeDescr
from ..generic.v0_3 import CiteEntry as CiteEntry
from ..generic.v0_3 import (
    DocumentationSource,
    GenericDescrBase,
    _author_conv,  # pyright: ignore[reportPrivateUsage]
    _maintainer_conv,  # pyright: ignore[reportPrivateUsage]
)
from ..generic.v0_3 import Doi as Doi
from ..generic.v0_3 import LinkedResource as LinkedResource
from ..generic.v0_3 import Maintainer as Maintainer
from ..generic.v0_3 import OrcidId as OrcidId
from ..generic.v0_3 import RelativeFilePath as RelativeFilePath
from ..generic.v0_3 import ResourceId as ResourceId
from ..generic.v0_3 import Uploader as Uploader
from ..generic.v0_3 import Version as Version
from .v0_2 import DatasetDescr as DatasetDescr02


class DatasetDescr(GenericDescrBase, title="bioimage.io dataset specification"):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    type: Literal["dataset"] = "dataset"

    id: Optional[DatasetId] = None
    """Model zoo (bioimage.io) wide, unique identifier (assigned by bioimage.io)"""

    parent: Optional[DatasetId] = None
    """The description from which this one is derived"""

    source: Optional[HttpUrl] = None
    """"URL to the source of the dataset."""

    @model_validator(mode="before")
    @classmethod
    def _convert(cls, data: Dict[str, Any], /) -> Dict[str, Any]:
        if (
            data.get("type") == "dataset"
            and isinstance(fv := data.get("format_version"), str)
            and fv.startswith("0.2.")
        ):
            old = DatasetDescr02.load(data)
            if isinstance(old, InvalidDescr):
                return data

            return cast(
                Dict[str, Any],
                (cls if TYPE_CHECKING else dict)(
                    attachments=(
                        []
                        if old.attachments is None
                        else [FileDescr(source=f) for f in old.attachments.files]
                    ),
                    authors=[
                        _author_conv.convert_as_dict(a) for a in old.authors
                    ],  # pyright: ignore[reportArgumentType]
                    badges=old.badges,
                    cite=[
                        {"text": c.text, "doi": c.doi, "url": c.url} for c in old.cite
                    ],  # pyright: ignore[reportArgumentType]
                    config=old.config,
                    covers=old.covers,
                    description=old.description,
                    documentation=cast(DocumentationSource, old.documentation),
                    format_version="0.3.0",
                    git_repo=old.git_repo,  # pyright: ignore[reportArgumentType]
                    icon=old.icon,
                    id=old.id,
                    license=old.license,  # type: ignore
                    links=old.links,
                    maintainers=[
                        _maintainer_conv.convert_as_dict(m) for m in old.maintainers
                    ],  # pyright: ignore[reportArgumentType]
                    name=old.name,
                    source=old.source,
                    tags=old.tags,
                    type=old.type,
                    uploader=old.uploader,
                    version=old.version,
                    **(old.model_extra or {}),
                ),
            )

        return data


class LinkedDataset(Node):
    """Reference to a bioimage.io dataset."""

    id: DatasetId
    """A valid dataset `id` from the bioimage.io collection."""

    version_number: int
    """version number (n-th published version, not the semantic version) of linked dataset"""
