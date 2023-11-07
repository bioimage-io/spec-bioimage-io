from typing import Literal

from pydantic import HttpUrl as HttpUrl

from bioimageio.spec._internal.types import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec._internal.types import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_3 import Attachment as Attachment
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import Badge as Badge
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import GenericBase, WithGenericFormatVersion
from bioimageio.spec.generic.v0_3 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.notebook.v0_2 import NotebookSource


class Notebook(GenericBase, WithGenericFormatVersion, title="bioimage.io notebook specification"):
    """Bioimage.io description of a Jupyter notebook."""

    type: Literal["notebook"] = "notebook"

    source: NotebookSource
    """The Jupyter notebook"""
