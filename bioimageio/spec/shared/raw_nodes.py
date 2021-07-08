"""shared raw nodes that shared transformer act on"""
import dataclasses
import pathlib
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING, Union
from urllib.parse import urlparse
from urllib.request import url2pathname

from marshmallow.utils import _Missing

try:
    from typing import get_args, get_origin
except ImportError:
    from typing_extensions import get_args, get_origin

from .common import get_args
from marshmallow import missing

if TYPE_CHECKING:
    from .schema import SharedBioImageIOSchema


@dataclass
class Node:
    def __post_init__(self):
        for f in dataclasses.fields(self):
            if getattr(self, f.name) is missing and (
                get_origin(f.type) is not Union or not isinstance(missing, get_args(f.type))
            ):
                raise TypeError(f"{self.__class__}.__init__() missing required argument: '{f.name}'")


@dataclass
class URI(Node):  # todo: do not allow relative path and use Union[Path, URI] instead
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
class SpecURI(URI):
    spec_schema: "SharedBioImageIOSchema" = missing


@dataclass
class ImportableSourceFile(Node):
    source_file: URI = missing
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
