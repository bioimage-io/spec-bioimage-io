from typing import Literal, Optional, Union

from typing_extensions import Annotated

from .._internal.common_nodes import Node
from .._internal.io import WithSuffix
from .._internal.io_basics import AbsoluteFilePath as AbsoluteFilePath
from .._internal.url import HttpUrl
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


class NotebookId(ResourceId):
    pass


_WithNotebookSuffix = WithSuffix(".ipynb", case_sensitive=True)
NotebookSource = Union[
    Annotated[HttpUrl, _WithNotebookSuffix],
    Annotated[AbsoluteFilePath, _WithNotebookSuffix],
    Annotated[RelativeFilePath, _WithNotebookSuffix],
]


class NotebookDescr(GenericDescrBase, title="bioimage.io notebook specification"):
    """Bioimage.io description of a Jupyter Notebook."""

    type: Literal["notebook"] = "notebook"

    id: Optional[NotebookId] = None
    """bioimage.io-wide unique resource identifier
    assigned by bioimage.io; version **un**specific."""

    source: NotebookSource
    """The Jupyter notebook"""


class LinkedNotebook(Node):
    """Reference to a bioimage.io notebook."""

    id: NotebookId
    """A valid notebook `id` from the bioimage.io collection."""

    version_number: Optional[int] = None
    """version number (n-th published version, not the semantic version) of linked notebook"""
