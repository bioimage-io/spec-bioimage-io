# autogen: start
from typing import Union

from . import v0_2, v0_3
from .v0_3 import Application

__all__ = ["v0_2", "v0_3", "Application"]

AnyApplication = Union[v0_3.Application, v0_2.Application]
# autogen: stop
