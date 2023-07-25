from typing import Literal

from pydantic import ConfigDict

from bioimageio.spec.generic.v0_2 import GenericBase


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


AnyNotebook = Notebook
