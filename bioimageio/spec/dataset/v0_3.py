from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, cast

from pydantic import model_validator

from bioimageio.spec._internal.base_nodes import InvalidDescr, Node
from bioimageio.spec._internal.types import DatasetId as DatasetId
from bioimageio.spec.dataset import v0_2
from bioimageio.spec.generic.v0_3 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import (
    DocumentationSource,
    GenericDescrBase,
    _author_conv,  # pyright: ignore[reportPrivateUsage]
    _maintainer_conv,  # pyright: ignore[reportPrivateUsage]
)
from bioimageio.spec.generic.v0_3 import Doi as Doi
from bioimageio.spec.generic.v0_3 import FileDescr as FileDescr
from bioimageio.spec.generic.v0_3 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_3 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3 import OrcidId as OrcidId
from bioimageio.spec.generic.v0_3 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_3 import ResourceId as ResourceId
from bioimageio.spec.generic.v0_3 import Sha256 as Sha256
from bioimageio.spec.generic.v0_3 import Uploader as Uploader


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
            old = v0_2.DatasetDescr.load(data)
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
                    cite=old.cite,
                    config=old.config,
                    covers=old.covers,
                    description=old.description,
                    documentation=cast(DocumentationSource, old.documentation),
                    format_version="0.3.0",
                    git_repo=old.git_repo,
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

    version_nr: int
    """version number (nth published version, not the semantic version) of linked dataset"""
