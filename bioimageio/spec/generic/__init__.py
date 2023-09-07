# autogen: start
from typing import Union

from pydantic import Field
from typing_extensions import Annotated

from . import v0_2, v0_3
from .v0_3 import Generic

__all__ = ["v0_2", "v0_3", "Generic"]

AnyGeneric = Annotated[Union[v0_2.Generic, v0_3.Generic], Field(discriminator="format_version")]
# autogen: stop
