from typing import Literal

from pydantic import ConfigDict
from typing_extensions import Annotated

from bioimageio.spec._internal.field_validation import WithSuffix
from bioimageio.spec.generic.v0_2 import GenericBase
from bioimageio.spec.types import FileSource


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
