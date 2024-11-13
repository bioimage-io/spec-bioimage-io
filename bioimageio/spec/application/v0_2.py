from typing import Literal, Optional

from pydantic import Field
from typing_extensions import Annotated

from .._internal.common_nodes import Node
from .._internal.io_basics import AbsoluteFilePath as AbsoluteFilePath
from .._internal.types import ImportantFileSource
from .._internal.url import HttpUrl as HttpUrl
from ..generic.v0_2 import VALID_COVER_IMAGE_EXTENSIONS as VALID_COVER_IMAGE_EXTENSIONS
from ..generic.v0_2 import AttachmentsDescr as AttachmentsDescr
from ..generic.v0_2 import Author as Author
from ..generic.v0_2 import BadgeDescr as BadgeDescr
from ..generic.v0_2 import CiteEntry as CiteEntry
from ..generic.v0_2 import Doi as Doi
from ..generic.v0_2 import GenericDescrBase
from ..generic.v0_2 import LinkedResource as LinkedResource
from ..generic.v0_2 import Maintainer as Maintainer
from ..generic.v0_2 import OrcidId as OrcidId
from ..generic.v0_2 import RelativeFilePath as RelativeFilePath
from ..generic.v0_2 import ResourceId as ResourceId
from ..generic.v0_2 import Uploader as Uploader
from ..generic.v0_2 import Version as Version


class ApplicationId(ResourceId):
    pass


class ApplicationDescr(GenericDescrBase, title="bioimage.io application specification"):
    """Bioimage.io description of an application."""

    type: Literal["application"] = "application"

    id: Optional[ApplicationId] = None
    """bioimage.io-wide unique resource identifier
    assigned by bioimage.io; version **un**specific."""

    source: Annotated[
        Optional[ImportantFileSource],
        Field(description="URL or path to the source of the application"),
    ] = None
    """The primary source of the application"""


class LinkedApplication(Node):
    """Reference to a bioimage.io application."""

    id: ApplicationId
    """A valid application `id` from the bioimage.io collection."""

    version_number: Optional[int] = None
    """version number (n-th published version, not the semantic version) of linked application"""
