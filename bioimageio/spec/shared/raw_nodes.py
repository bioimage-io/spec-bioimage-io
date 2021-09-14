"""shared raw nodes that shared transformers act on

raw nodes are the deserialized equivalent to the content of any RDF.
serialization and deserialization are defined in schema:
RDF <--schema--> raw nodes
"""
import dataclasses
import distutils.version
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
class ResourceDescription(RawNode):
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
    root_path: pathlib.Path = pathlib.Path()  # note: `root_path` is not officially part of the spec,
    #                                                  but any RDF has it as it is the folder containing the rdf.yaml


@dataclass
class URI(RawNode):  # todo: do not allow relative path and use Union[Path, URI] instead
    """URI as scheme:[//authority]path[?query][#fragment] or relative path (only path is set)"""

    uri_string: Optional[str] = None  # for convenience: init from string; this should be dataclasses.InitVar,
    # but due to a bug in dataclasses.replace in py3.7 (https://bugs.python.org/issue36470) it is not.
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

    def __post_init__(self):
        uri_string = self.uri_string  # should be InitVar, see comment at definition above
        if uri_string is None:
            if self.path is missing or (not self.scheme and any([self.authority, self.query, self.fragment])):
                raise ValueError("Invalid URI or relative path")
        elif str(self):
            raise ValueError(f"Either specify uri_string(={uri_string}) or uri components (={str(self)})")
        elif isinstance(uri_string, str):
            self.uri_string = None  # not required if 'uri_string' would be InitVar, see comment at definition above
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
class Dependencies(RawNode):
    _include_in_package = ("file",)

    manager: str = missing
    file: Union[URI, pathlib.Path] = missing

    def __str__(self):
        if isinstance(self.file, pathlib.Path):
            assert not self.file.is_absolute(), self.file

        return f"{self.manager}:{self.file}"


@dataclass
class ParametrizedInputShape(RawNode):
    min: List[float] = missing
    step: List[float] = missing

    def __len__(self):
        return len(self.min)


@dataclass
class ImplicitOutputShape(RawNode):
    reference_tensor: str = missing
    scale: List[float] = missing
    offset: List[int] = missing

    def __len__(self):
        return len(self.scale)


@dataclass
class ImportableModule(RawNode):
    module_name: str = missing
    callable_name: str = missing


@dataclass
class ImportableSourceFile(RawNode):
    _include_in_package = ("source_file",)

    callable_name: str = missing
    source_file: URI = missing


ImportableSource = Union[ImportableModule, ImportableSourceFile]
