"""shared nodes that shared transformer act on"""

from .raw_nodes import *


@dataclass
class ImportedSource:
    factory: callable

    def __call__(self, *args, **kwargs):
        return self.factory(*args, **kwargs)
