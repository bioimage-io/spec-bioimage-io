"""shared raw nodes that shared transformer act on"""
import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

try:
    from typing import get_args, get_origin
except ImportError:
    from typing_extensions import get_args, get_origin

from marshmallow import missing

try:
    from typing import Literal, get_args
except ImportError:
    from typing_extensions import Literal, get_args  # noqa


@dataclass
class Node:
    def __post_init__(self):
        for f in dataclasses.fields(self):
            if getattr(self, f.name) is missing and (
                get_origin(f.type) is not Union or not isinstance(missing, get_args(f.type))
            ):
                raise TypeError(f"{self.__class__}.__init__() missing required argument: '{f.name}'")


@dataclass
class URI(Node):
    """URI as  scheme:[//authority]path[?query][#fragment]"""

    scheme: str = missing
    authority: str = missing
    path: str = missing
    query: str = missing
    fragment: str = missing

    def __str__(self):
        """scheme:[//authority]path[?query][#fragment]"""
        return (
            (self.scheme + ":" if self.scheme else "")
            + ("//" + self.authority if self.authority else "")
            + self.path
            + ("?" + self.query if self.query else "")
            + ("#" + self.fragment if self.fragment else "")
        )


@dataclass
class ImportablePath(Node):
    filepath: Path = missing
    callable_name: str = missing


@dataclass
class ImportableModule(Node):
    module_name: str = missing
    callable_name: str = missing


@dataclass
class ImplicitInputShape(Node):
    min: List[float] = missing
    step: List[float] = missing

    def __len__(self):
        return len(self.min)


@dataclass
class ImplicitOutputShape(Node):
    reference_input: str = missing
    scale: List[float] = missing
    offset: List[int] = missing

    def __len__(self):
        return len(self.scale)
