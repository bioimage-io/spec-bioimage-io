# autogen: start
from typing import Union

from pydantic import Field
from typing_extensions import Annotated

from . import v0_2, v0_3
from .v0_3 import Application

__all__ = ["v0_2", "v0_3", "Application"]

AnyApplication = Annotated[Union[v0_2.Application, v0_3.Application], Field(discriminator="format_version")]
# autogen: stop
