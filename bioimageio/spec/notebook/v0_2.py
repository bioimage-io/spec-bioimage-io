from typing import Literal, Union

from typing_extensions import Annotated

from bioimageio.spec._internal.types import AbsoluteFilePath, RelativeFilePath
from bioimageio.spec._internal.types.field_validation import WithSuffix
from bioimageio.spec.generic.v0_2 import AttachmentsDescr as AttachmentsDescr
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import GenericDescrBase, HttpUrl
from bioimageio.spec.generic.v0_2 import LinkedResourceDescr as LinkedResourceDescr
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_2 import ResourceId as ResourceId

_WithNotebookSuffix = WithSuffix(".ipynb", case_sensitive=True)
NotebookSource = Union[
    Annotated[HttpUrl, _WithNotebookSuffix],
    Annotated[AbsoluteFilePath, _WithNotebookSuffix],
    Annotated[RelativeFilePath, _WithNotebookSuffix],
]


class NotebookDescr(GenericDescrBase, title="bioimage.io notebook specification"):
    """Bioimage.io description of a Jupyter Notebook."""

    type: Literal["notebook"] = "notebook"

    source: NotebookSource
    """The Jupyter notebook"""
