"""shared nodes that shared transformer act on"""
from collections.abc import Callable

from .raw_nodes import *


@dataclass
class ImportedSource:
    factory: Callable

    def __call__(self, *args, **kwargs):
        return self.factory(*args, **kwargs)
