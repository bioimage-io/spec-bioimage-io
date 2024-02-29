from typing import Literal, Optional

from pydantic import Field
from typing_extensions import Annotated

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.types import ApplicationId as ApplicationId
from bioimageio.spec._internal.types import ImportantFileSource
from bioimageio.spec.generic.v0_3 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import Doi as Doi
from bioimageio.spec.generic.v0_3 import FileDescr as FileDescr
from bioimageio.spec.generic.v0_3 import GenericDescrBase
from bioimageio.spec.generic.v0_3 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_3 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3 import OrcidId as OrcidId
from bioimageio.spec.generic.v0_3 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_3 import ResourceId as ResourceId
from bioimageio.spec.generic.v0_3 import Sha256 as Sha256
from bioimageio.spec.generic.v0_3 import Uploader as Uploader


class ApplicationDescr(GenericDescrBase, title="bioimage.io application specification"):
    """Bioimage.io description of an application."""

    type: Literal["application"] = "application"

    id: Optional[ApplicationId] = None
    """Model zoo (bioimage.io) wide, unique identifier (assigned by bioimage.io)"""

    parent: Optional[ApplicationId] = None
    """The description from which this one is derived"""

    source: Annotated[
        Optional[ImportantFileSource],
        Field(description="URL or path to the source of the application"),
    ] = None
    """The primary source of the application"""


class LinkedApplication(Node):
    """Reference to a bioimage.io application."""

    id: ApplicationId
    """A valid application `id` from the bioimage.io collection."""

    version_nr: int
    """version number (nth published version, not the semantic version) of linked application"""
