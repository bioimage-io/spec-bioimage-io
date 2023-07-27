# autogen: start
from typing import Union

from . import v0_2, v0_3
from .v0_3 import Collection

__all__ = ["v0_2", "v0_3", "Collection"]

AnyCollection = Union[v0_3.Collection, v0_2.Collection]
# autogen: stop
