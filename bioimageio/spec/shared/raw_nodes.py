# DEPRECATED
"""shared raw nodes that shared transformers act on

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
import dataclasses
import os

import packaging.version
import pathlib
from dataclasses import dataclass
from typing import ClassVar, List, Optional, Sequence, Union
from urllib.parse import urlparse
from urllib.request import url2pathname

from marshmallow import missing
from marshmallow.utils import _Missing

try:
    from typing import get_args, get_origin
except ImportError:
    from typing_extensions import get_args, get_origin  # type: ignore


@dataclass
class Dependencies(RawNode):
    _include_in_package = ("file",)

    manager: str = missing
    file: Union[URI, pathlib.Path] = missing

    def __str__(self):
        return f"{self.manager}:{self.file}"


@dataclass
class ParametrizedInputShape(RawNode):
    min: List[int] = missing
    step: List[int] = missing

    def __len__(self):
        return len(self.min)


@dataclass
class ImplicitOutputShape(RawNode):
    reference_tensor: str = missing
    scale: List[Union[float, None]] = missing
    offset: List[float] = missing

    def __len__(self):
        return len(self.scale)
