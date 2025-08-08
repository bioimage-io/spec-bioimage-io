from typing import TYPE_CHECKING, ClassVar, Literal, Optional

from pydantic import Field
from typing_extensions import Annotated

from .._internal.io import FileDescr as FileDescr
from .._internal.io_basics import Sha256 as Sha256
from .._internal.types import FAIR, FileSource_
from .._internal.url import HttpUrl as HttpUrl
from ..generic.v0_3 import VALID_COVER_IMAGE_EXTENSIONS as VALID_COVER_IMAGE_EXTENSIONS
from ..generic.v0_3 import Author as Author
from ..generic.v0_3 import BadgeDescr as BadgeDescr
from ..generic.v0_3 import BioimageioConfig as BioimageioConfig
from ..generic.v0_3 import CiteEntry as CiteEntry
from ..generic.v0_3 import Config as Config
from ..generic.v0_3 import DeprecatedLicenseId as DeprecatedLicenseId
from ..generic.v0_3 import Doi as Doi
from ..generic.v0_3 import GenericDescrBase, LinkedResourceBase, ResourceId
from ..generic.v0_3 import LicenseId as LicenseId
from ..generic.v0_3 import LinkedResource as LinkedResource
from ..generic.v0_3 import Maintainer as Maintainer
from ..generic.v0_3 import OrcidId as OrcidId
from ..generic.v0_3 import RelativeFilePath as RelativeFilePath
from ..generic.v0_3 import Uploader as Uploader
from ..generic.v0_3 import Version as Version


class ApplicationId(ResourceId):
    pass


class ApplicationDescr(GenericDescrBase):
    """Bioimage.io description of an application."""

    implemented_type: ClassVar[Literal["application"]] = "application"
    if TYPE_CHECKING:
        type: Literal["application"] = "application"
    else:
        type: Literal["application"]

    id: Optional[ApplicationId] = None
    """bioimage.io-wide unique resource identifier
    assigned by bioimage.io; version **un**specific."""

    parent: Optional[ApplicationId] = None
    """The description from which this one is derived"""

    source: Annotated[
        FAIR[Optional[FileSource_]],
        Field(description="URL or path to the source of the application"),
    ] = None
    """The primary source of the application"""


class LinkedApplication(LinkedResourceBase):
    """Reference to a bioimage.io application."""

    id: ApplicationId
    """A valid application `id` from the bioimage.io collection."""
