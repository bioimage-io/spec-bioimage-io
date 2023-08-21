from typing import Literal, Union

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from bioimageio.spec._internal._validate import WithSuffix
from bioimageio.spec.generic.v0_3 import GenericBase
from bioimageio.spec.notebook import v0_2
from bioimageio.spec.types import FileSource


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


AnyNotebook = Annotated[Union[v0_2.Notebook, Notebook], Field(discriminator="format_version")]
