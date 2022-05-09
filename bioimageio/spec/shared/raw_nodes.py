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
class URI(RawNode):
    """URI as scheme:[//authority]path[?query][#fragment]"""

    uri_string: Optional[str] = None  # for convenience: init from string; this should be dataclasses.InitVar,
    # but due to a bug in dataclasses.replace in py3.7 (https://bugs.python.org/issue36470) it is not.
    scheme: str = missing
    authority: str = ""
    path: str = missing
    query: str = ""
    fragment: str = ""

    def __str__(self):
        """scheme:[//authority]path[?query][#fragment]"""
        return (
            self.scheme
            + ":"
            + ("//" + self.authority if self.authority else "")
            + self.path
            + ("?" + self.query if self.query else "")
            + ("#" + self.fragment if self.fragment else "")
        )

    def __truediv__(self, other):
        """Analog to pathlib.Path truediv concatenates the path element of a URI with a string or relative path.
        Absolute paths or URIs are not concatenated, but returned instead of self analog to pathlib.Path() / <abs path>
        """
        if isinstance(other, (str, os.PathLike)):
            other = pathlib.Path(other)
            if other.is_absolute():
                return other
            else:
                other = pathlib.PurePosixPath(other)
                return dataclasses.replace(
                    self, path=(pathlib.PurePosixPath(self.path) / other).as_posix(), uri_string=None
                )
        elif isinstance(other, URI):
            return other
        else:
            raise TypeError(f"Unexpected type {type(other)} of {other}.")

    @property
    def parent(self):
        path_parent = pathlib.PurePosixPath(self.path).parent.as_posix()
        return dataclasses.replace(self, path=path_parent, uri_string=None)

    def __post_init__(self):
        uri_string = self.uri_string  # should be InitVar, see comment at definition above
        uri_components = [self.scheme, self.authority, self.path, self.query, self.fragment]
        if uri_string is None:
            pass
        elif any(uri_components):
            raise ValueError(f"Either specify uri_string(={uri_string}) or uri components(={uri_components})")
        elif isinstance(uri_string, str):
            self.uri_string = None  # not required if 'uri_string' would be InitVar, see comment at definition above
            uri = urlparse(uri_string)
            if uri.scheme == "file":
                # account for leading '/' for windows paths, e.g. '/C:/folder'
                # see https://stackoverflow.com/questions/43911052/urlparse-on-a-windows-file-scheme-uri-leaves-extra-slash-at-start
                path = pathlib.Path(url2pathname(uri.path)).as_posix()
            else:
                path = uri.path

            self.scheme = uri.scheme
            self.authority = uri.netloc
            self.path = path
            self.query = uri.query
            self.fragment = uri.fragment
        else:
            raise TypeError(uri_string)

        if not self.scheme:
            raise ValueError("Empty URI scheme component")
        elif len(self.scheme) == 1:
            raise ValueError(f"Invalid URI scheme of len 1: {self.scheme}")  # fail for windows paths with drive letter

        super().__post_init__()


@dataclass
class ResourceDescription(RawNode):
    """Bare minimum for resource description nodes usable with the shared IO_Base class.
    This is not part of any specification for the BioImage.IO Model Zoo and, e.g.
    not to be confused with the definition of the general RDF.
    """

    format_version: str = missing
    name: str = missing
    type: str = missing
    version: Union[_Missing, packaging.version.Version] = missing
    root_path: Union[pathlib.Path, URI] = pathlib.Path()  # note: `root_path` is not officially part of the spec,
    #                                                    but any RDF has it as it is the folder containing the rdf.yaml


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
