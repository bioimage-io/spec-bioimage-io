from typing import TYPE_CHECKING, ClassVar, Literal, Optional

from .._internal.io import FileDescr as FileDescr
from .._internal.io_basics import Sha256 as Sha256
from .._internal.url import HttpUrl as HttpUrl
from ..generic.v0_3 import VALID_COVER_IMAGE_EXTENSIONS as VALID_COVER_IMAGE_EXTENSIONS
from ..generic.v0_3 import Author as Author
from ..generic.v0_3 import BadgeDescr as BadgeDescr
from ..generic.v0_3 import BioimageioConfig as BioimageioConfig
from ..generic.v0_3 import CiteEntry as CiteEntry
from ..generic.v0_3 import Config as Config
from ..generic.v0_3 import DeprecatedLicenseId as DeprecatedLicenseId
from ..generic.v0_3 import Doi as Doi
from ..generic.v0_3 import GenericDescrBase, LinkedResourceBase
from ..generic.v0_3 import LicenseId as LicenseId
from ..generic.v0_3 import LinkedResource as LinkedResource
from ..generic.v0_3 import Maintainer as Maintainer
from ..generic.v0_3 import OrcidId as OrcidId
from ..generic.v0_3 import RelativeFilePath as RelativeFilePath
from ..generic.v0_3 import ResourceId as ResourceId
from ..generic.v0_3 import Uploader as Uploader
from ..generic.v0_3 import Version as Version
from .v0_2 import NotebookSource as NotebookSource


class NotebookId(ResourceId):
    pass


class NotebookDescr(GenericDescrBase):
    """Bioimage.io description of a Jupyter notebook."""

    implemented_type: ClassVar[Literal["notebook"]] = "notebook"
    if TYPE_CHECKING:
        type: Literal["notebook"] = "notebook"
    else:
        type: Literal["notebook"]

    id: Optional[NotebookId] = None
    """bioimage.io-wide unique resource identifier
    assigned by bioimage.io; version **un**specific."""

    parent: Optional[NotebookId] = None
    """The description from which this one is derived"""

    source: NotebookSource
    """The Jupyter notebook"""


class LinkedNotebook(LinkedResourceBase):
    """Reference to a bioimage.io notebook."""

    id: NotebookId
    """A valid notebook `id` from the bioimage.io collection."""
