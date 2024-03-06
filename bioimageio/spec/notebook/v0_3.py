from typing import Literal, Optional

from .._internal.common_nodes import Node
from .._internal.io import FileDescr as FileDescr
from .._internal.io import Sha256 as Sha256
from .._internal.io_basics import AbsoluteFilePath as AbsoluteFilePath
from .._internal.types import NotebookId as NotebookId
from .._internal.url import HttpUrl as HttpUrl
from ..generic.v0_3 import Author as Author
from ..generic.v0_3 import BadgeDescr as BadgeDescr
from ..generic.v0_3 import CiteEntry as CiteEntry
from ..generic.v0_3 import Doi as Doi
from ..generic.v0_3 import GenericDescrBase
from ..generic.v0_3 import LinkedResource as LinkedResource
from ..generic.v0_3 import Maintainer as Maintainer
from ..generic.v0_3 import OrcidId as OrcidId
from ..generic.v0_3 import RelativeFilePath as RelativeFilePath
from ..generic.v0_3 import ResourceId as ResourceId
from ..generic.v0_3 import Uploader as Uploader
from ..generic.v0_3 import Version as Version
from .v0_2 import NotebookSource as NotebookSource


class NotebookDescr(GenericDescrBase, title="bioimage.io notebook specification"):
    """Bioimage.io description of a Jupyter notebook."""

    type: Literal["notebook"] = "notebook"

    id: Optional[NotebookId] = None
    """Model zoo (bioimage.io) wide, unique identifier (assigned by bioimage.io)"""

    parent: Optional[NotebookId] = None
    """The description from which this one is derived"""

    source: NotebookSource
    """The Jupyter notebook"""


class LinkedNotebook(Node):
    """Reference to a bioimage.io notebook."""

    id: NotebookId
    """A valid notebook `id` from the bioimage.io collection."""

    version_number: int
    """version number (n-th published version, not the semantic version) of linked notebook"""
