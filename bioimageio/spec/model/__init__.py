# autogen: start
from typing import Union

from . import v0_4, v0_5
from .v0_5 import Model

__all__ = ["v0_4", "v0_5", "Model"]

AnyModel = Union[v0_5.Model, v0_4.Model]
# autogen: stop
