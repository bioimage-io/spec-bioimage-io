# autogen: start
from typing import Union

from pydantic import Field
from typing_extensions import Annotated

from . import v0_2, v0_3
from .v0_3 import Notebook

__all__ = ["v0_2", "v0_3", "Notebook"]

AnyNotebook = Annotated[Union[v0_2.Notebook, v0_3.Notebook], Field(discriminator="format_version")]
# autogen: stop
