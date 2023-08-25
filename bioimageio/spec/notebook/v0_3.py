from typing import Literal, Union

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from bioimageio.spec._internal.field_validation import WithSuffix
from bioimageio.spec.generic.v0_3 import *
from bioimageio.spec.generic.v0_3 import GenericBase
from bioimageio.spec.types import FileSource

__all__ = [
    "Attachments",
    "Author",
    "Badge",
    "CiteEntry",
    "LinkedResource",
    "Maintainer",
    "Notebook",
]


class Notebook(GenericBase):
    """Bioimage.io description of a Jupyter notebook."""

    model_config = ConfigDict(
        {
            **GenericBase.model_config,
            **ConfigDict(title="bioimage.io notebook specification"),
        }
    )
    """pydantic model_config"""

    type: Literal["notebook"] = "notebook"

    source: Annotated[FileSource, WithSuffix(".ipynb", case_sensitive=True)]
    """The Jupyter notebook"""
