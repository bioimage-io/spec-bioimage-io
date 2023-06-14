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
class RawNode:
    _include_in_package: ClassVar[Sequence[str]] = tuple()  # todo: move to field meta data

    def __post_init__(self):
        for f in dataclasses.fields(self):
            if getattr(self, f.name) is missing and (
                get_origin(f.type) is not Union or not isinstance(missing, get_args(f.type))
            ):
                raise TypeError(f"{self.__class__}.__init__() missing required argument: '{f.name}'")

        field_names = [f.name for f in dataclasses.fields(self)]
        for incl_in_package in self._include_in_package:
            assert incl_in_package in field_names


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


@dataclass
class ImportableModule(RawNode):
    module_name: str = missing
    callable_name: str = missing

    def __str__(self):
        return f"{self.module_name}:{self.callable_name}"


@dataclass
class LocalImportableModule(ImportableModule):
    """intermediate between raw_nodes.ImportableModule and core.resource_io.nodes.ImportedSource.

    Used by SourceNodeTransformer
    """

    root_path: pathlib.Path = missing


@dataclass
class ImportableSourceFile(RawNode):
    _include_in_package = ("source_file",)

    callable_name: str = missing
    source_file: Union[URI, pathlib.Path] = missing

    def __str__(self):
        return f"{self.source_file}:{self.callable_name}"


@dataclass
class ResolvedImportableSourceFile(ImportableSourceFile):
    """intermediate between raw_nodes.ImportableSourceFile and core.resource_io.nodes.ImportedSource.

    Used by SourceNodeTransformer
    """

    source_file: pathlib.Path = missing


ImportableSource = Union[ImportableModule, ImportableSourceFile, ResolvedImportableSourceFile, LocalImportableModule]
