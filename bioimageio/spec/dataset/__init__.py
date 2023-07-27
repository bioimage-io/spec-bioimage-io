# autogen: start
from typing import Union

from . import v0_2, v0_3
from .v0_3 import Dataset

__all__ = ["v0_2", "v0_3", "Dataset"]

AnyDataset = Union[v0_3.Dataset, v0_2.Dataset]
# autogen: stop
