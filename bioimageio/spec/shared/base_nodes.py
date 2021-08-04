"""base classes with implementations for nodes and raw nodes.
This avoids:
 - nodes inheriting from raw nodes
 - raw nodes inheriting from nodes
 - reimplementing equivalent logic for nodes and raw nodes where they overlap
"""
import dataclasses
import distutils.version
import pathlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Union
from urllib.parse import urlparse
from urllib.request import url2pathname

from marshmallow.utils import _Missing

from .common import get_args, get_origin
from marshmallow import missing


@dataclass
class NodeBase:
    def __post_init__(self):
        from . import nodes, raw_nodes

        if not isinstance(self, (nodes.Node, raw_nodes.RawNode)):
            raise TypeError("base nodes should not be instantiated!")

        for f in dataclasses.fields(self):
            if getattr(self, f.name) is missing and (
                get_origin(f.type) is not Union or not isinstance(missing, get_args(f.type))
            ):
                raise TypeError(f"{self.__class__}.__init__() missing required argument: '{f.name}'")


@dataclass
class ResourceDescription(NodeBase):
    """Bare minimum for resource description nodes usable with the shared IO_Base class.
    This is not part of any specification for the BioImage.IO Model Zoo and, e.g.
    not to be confused with the definition of the general RDF.
    (Future) RDF nodes do not have to inherit from this node, but will have to account for deviations in their IO
    implementation.
    """

    format_version: str = missing
    name: str = missing
    type: str = missing
    version: Union[_Missing, distutils.version.StrictVersion] = missing


@dataclass
class URI(NodeBase):  # todo: do not allow relative path and use Union[Path, URI] instead
    """URI as scheme:[//authority]path[?query][#fragment] or relative path (only path is set)"""

    uri_string: dataclasses.InitVar[Optional[str]] = None  # for convenience: init from string
    scheme: str = ""
    authority: str = ""
    path: str = missing
    query: str = ""
    fragment: str = ""

    def __str__(self):
        """[scheme:][//authority]path[?query][#fragment]"""
        return (
            (self.scheme + ":" if self.scheme else "")
            + ("//" + self.authority if self.authority else "")
            + (self.path if self.path else "")
            + ("?" + self.query if self.query else "")
            + ("#" + self.fragment if self.fragment else "")
        )

    def __post_init__(self, uri_string):
        if uri_string is None:
            if self.path is missing or (not self.scheme and any([self.authority, self.query, self.fragment])):
                raise ValueError("Invalid URI or relative path")
        elif str(self):
            raise ValueError(f"Either specify uri_string(={uri_string}) or uri components (={str(self)})")
        elif isinstance(uri_string, str):
            uri = urlparse(uri_string)
            if uri.scheme == "file":
                # account for leading '/' for windows paths, e.g. '/C:/folder'
                # see https://stackoverflow.com/questions/43911052/urlparse-on-a-windows-file-scheme-uri-leaves-extra-slash-at-start
                path = url2pathname(uri.path)
            else:
                path = uri.path

            self.scheme = uri.scheme
            self.authority = uri.netloc
            self.path = path
            self.query = uri.query
            self.fragment = uri.fragment
        else:
            raise TypeError(uri_string)
        # no scheme := relative path
        # also check for absolute paths in posix style (even on windows, as '/lala' is resolved to absolute Path
        # 'C:/lala' on windows, while '/lala' is a relative path on windows
        if not self.scheme and (
            pathlib.Path(self.path).is_absolute() or pathlib.PurePosixPath(self.path).is_absolute()
        ):
            raise ValueError("Invalid URI or relative path. (use URI with scheme 'file' for absolute file paths)")

        super().__post_init__()


# to pass mypy:
# separate dataclass and abstract class as a workaround for abstract dataclasses
# from https://github.com/python/mypy/issues/5374#issuecomment-650656381
@dataclass
class _Dependencies(NodeBase):
    manager: str = missing


class Dependencies(_Dependencies, ABC):
    @property
    @abstractmethod
    def file(self):
        ...

    def __str__(self):
        if isinstance(self.file, pathlib.Path):
            assert not self.file.is_absolute(), self.file

        return f"{self.manager}:{self.file}"


@dataclass
class ImplicitInputShape(NodeBase):
    min: List[float] = missing
    step: List[float] = missing

    def __len__(self):
        return len(self.min)


@dataclass
class ImplicitOutputShape(NodeBase):
    reference_input: str = missing
    scale: List[float] = missing
    offset: List[int] = missing

    def __len__(self):
        return len(self.scale)


@dataclass
class ImportableModule(NodeBase):
    module_name: str = missing
    callable_name: str = missing


# to pass mypy:
# separate dataclass and abstract class as a workaround for abstract dataclasses
# from https://github.com/python/mypy/issues/5374#issuecomment-650656381
@dataclass
class _ImportableSourceFile(NodeBase):
    callable_name: str = missing


class ImportableSourceFile(_ImportableSourceFile, ABC):
    @property
    @abstractmethod
    def source_file(self):
        ...
