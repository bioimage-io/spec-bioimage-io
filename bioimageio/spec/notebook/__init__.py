# autogen: start
from typing import Union

from . import v0_2, v0_3
from .v0_3 import Notebook

__all__ = ["v0_2", "v0_3", "Notebook"]

AnyNotebook = Union[v0_3.Notebook, v0_2.Notebook]
# autogen: stop
