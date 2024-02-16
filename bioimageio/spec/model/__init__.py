# autogen: start
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_4 as v0_4, v0_5 as v0_5
from .v0_5 import ModelDescr as ModelDescr

AnyModelDescr = Annotated[
    Union[v0_4.ModelDescr, v0_5.ModelDescr], Discriminator("format_version")
]
# autogen: stop
