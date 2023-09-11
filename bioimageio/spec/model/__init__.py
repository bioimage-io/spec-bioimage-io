# autogen: start
from typing import Union

from pydantic import Field
from typing_extensions import Annotated

from . import v0_4 as v0_4, v0_5 as v0_5
from .v0_5 import Model as Model

AnyModel = Annotated[Union[v0_4.Model, v0_5.Model], Field(discriminator="format_version")]
# autogen: stop
