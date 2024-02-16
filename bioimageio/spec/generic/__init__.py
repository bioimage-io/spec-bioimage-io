# autogen: start
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_2 as v0_2, v0_3 as v0_3
from .v0_3 import GenericDescr as GenericDescr

AnyGenericDescr = Annotated[Union[v0_2.GenericDescr, v0_3.GenericDescr], Discriminator("format_version")]
# autogen: stop
