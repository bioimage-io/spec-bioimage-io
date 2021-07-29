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

try:
    from typing import get_args, get_origin
except ImportError:
    from typing_extensions import get_args, get_origin

from .common import get_args
from marshmallow import missing


@dataclass
class NodeBase:
    def __post_init__(self):
        for f in dataclasses.fields(self):
            if getattr(self, f.name) is missing and (
                get_origin(f.type) is not Union or not isinstance(missing, get_args(f.type))
            ):
                raise TypeError(f"{self.__class__}.__init__() missing required argument: '{f.name}'")


@dataclass
class ResourceDescriptionBase(NodeBase):
    format_version: str = missing
    name: str = missing
    type: str = missing
    version: Union[_Missing, distutils.version.StrictVersion] = missing


@dataclass
class URI_Base(NodeBase):  # todo: do not allow relative path and use Union[Path, URI] instead
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


@dataclass
class DependenciesBase(NodeBase, ABC):
    manager: str = missing

    @property
    @abstractmethod
    def file(self):
        pass

    def __str__(self):
        if isinstance(self.file, pathlib.Path):
            assert not self.file.is_absolute(), self.file

        return f"{self.manager}:{self.file}"


@dataclass
class ImplicitInputShapeBase(NodeBase):
    min: List[float] = missing
    step: List[float] = missing

    def __len__(self):
        return len(self.min)


@dataclass
class ImplicitOutputShapeBase(NodeBase):
    reference_input: str = missing
    scale: List[float] = missing
    offset: List[int] = missing

    def __len__(self):
        return len(self.scale)


@dataclass
class ImportableModuleBase(NodeBase):
    module_name: str = missing
    callable_name: str = missing


@dataclass
class ImportableSourceFileBase(NodeBase, ABC):
    @property
    @abstractmethod
    def source_file(self):
        pass

    callable_name: str = missing
