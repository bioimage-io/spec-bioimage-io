from typing import Annotated, Literal, Union

from pydantic import ConfigDict, Field

from bioimageio.spec.generic.v0_3 import GenericBase
from bioimageio.spec.notebook import v0_2


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


AnyNotebook = Annotated[Union[v0_2.Notebook, Notebook], Field(discriminator="format_version")]
