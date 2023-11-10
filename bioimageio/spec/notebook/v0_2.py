from typing import Literal, Union

from pydantic import HttpUrl
from typing_extensions import Annotated

from bioimageio.spec._internal.types.field_validation import WithSuffix
from bioimageio.spec.generic.v0_2 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_2 import Attachments as Attachments
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import Badge as Badge
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import FileSource as FileSource
from bioimageio.spec.generic.v0_2 import GenericBase
from bioimageio.spec.generic.v0_2 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_2 import RelativeFilePath as RelativeFilePath

_WithNotebookSuffix = WithSuffix(".ipynb", case_sensitive=True)
NotebookSource = Union[
    Annotated[HttpUrl, _WithNotebookSuffix],
    Annotated[AbsoluteFilePath, _WithNotebookSuffix],
    Annotated[RelativeFilePath, _WithNotebookSuffix],
]


class Notebook(GenericBase, title="bioimage.io notebook specification"):
    """Bioimage.io description of a Jupyter Notebook."""

    type: Literal["notebook"] = "notebook"

    source: NotebookSource
    """The Jupyter notebook"""
