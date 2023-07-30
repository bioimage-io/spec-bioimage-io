from typing import Annotated, Literal

from pydantic import ConfigDict

from bioimageio.spec._internal._validate import WithSuffix
from bioimageio.spec.generic.v0_2 import GenericBase
from bioimageio.spec.shared.types import FileSource


class Notebook(GenericBase):
    """Bioimage.io description of a Jupyter Notebook."""

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


AnyNotebook = Notebook
