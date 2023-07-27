# autogen: start
from typing import Union

from . import v0_2, v0_3
from .v0_3 import Generic

__all__ = ["v0_2", "v0_3", "Generic"]

AnyGeneric = Union[v0_3.Generic, v0_2.Generic]
# autogen: stop
