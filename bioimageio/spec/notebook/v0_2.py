from typing import Literal

from bioimageio.spec.generic.v0_2 import GenericBase


class Notebook(GenericBase):
    """Bioimage.io description of a Jupyter Notebook."""

    model_config = {
        **GenericBase.model_config,
        **dict(title="bioimage.io notebook specification"),
    }
    """pydantic model_config"""

    type: Literal["notebook"] = "notebook"
