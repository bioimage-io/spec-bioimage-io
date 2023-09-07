from typing import Literal

from typing_extensions import Annotated

from bioimageio.spec._internal.field_validation import WithSuffix
from bioimageio.spec._internal.types import FileSource
from bioimageio.spec.generic.v0_3 import *
from bioimageio.spec.generic.v0_3 import GenericBase

__all__ = [
    "Attachments",
    "Author",
    "Badge",
    "CiteEntry",
    "LinkedResource",
    "Maintainer",
    "Notebook",
]


class Notebook(GenericBase, frozen=True, title="bioimage.io notebook specification"):
    """Bioimage.io description of a Jupyter notebook."""

    type: Literal["notebook"] = "notebook"

    source: Annotated[FileSource, WithSuffix(".ipynb", case_sensitive=True)]
    """The Jupyter notebook"""
