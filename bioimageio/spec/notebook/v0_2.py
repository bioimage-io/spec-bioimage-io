from typing import Literal, Optional, Union

from typing_extensions import Annotated

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.io_basics import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec._internal.io_validation import WithSuffix
from bioimageio.spec._internal.types import NotebookId as NotebookId
from bioimageio.spec.generic.v0_2 import AttachmentsDescr as AttachmentsDescr
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import Doi as Doi
from bioimageio.spec.generic.v0_2 import GenericDescrBase, HttpUrl
from bioimageio.spec.generic.v0_2 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_2 import OrcidId as OrcidId
from bioimageio.spec.generic.v0_2 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_2 import ResourceId as ResourceId
from bioimageio.spec.generic.v0_2 import Uploader as Uploader

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
    """Model zoo (bioimage.io) wide, unique identifier (assigned by bioimage.io)"""

    source: NotebookSource
    """The Jupyter notebook"""


class LinkedNotebook(Node):
    """Reference to a bioimage.io notebook."""

    id: NotebookId
    """A valid notebook `id` from the bioimage.io collection."""

    version_nr: Optional[int] = None
    """version number (n-th published version, not the semantic version) of linked notebook"""
