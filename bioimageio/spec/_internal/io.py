from __future__ import annotations

import pathlib
import sys
from dataclasses import dataclass
from datetime import date as _date
from datetime import datetime as _datetime
from functools import partial
from pathlib import Path, PurePath, PurePosixPath
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
    cast,
)
from urllib.parse import urlparse, urlsplit, urlunsplit

import pydantic
from pydantic import (
    AfterValidator,
    AnyUrl,
    DirectoryPath,
    FilePath,
    GetCoreSchemaHandler,
    SerializerFunctionWrapHandler,
    StringConstraints,
    TypeAdapter,
    WrapSerializer,
)
from pydantic_core import core_schema
from typing_extensions import Annotated, LiteralString, NotRequired, assert_never
from typing_extensions import TypeAliasType as _TypeAliasType

from bioimageio.spec._internal.base_nodes import ValidatedString
from bioimageio.spec._internal.io_basics import (
    ALL_BIOIMAGEIO_YAML_NAMES,
    AbsoluteDirectory,
    AbsoluteFilePath,
    FileName,
)
from bioimageio.spec._internal.validation_context import (
    HttpUrl as HttpUrl,  # defined in `validation_context` due to its dependence on `validation_context_var`
)
from bioimageio.spec._internal.validation_context import (
    validation_context_var,
)

if sys.version_info < (3, 10):
    SLOTS: Dict[str, bool] = {}
else:
    SLOTS = {"slots": True}


def extract_file_name(
    src: Union[pydantic.HttpUrl, HttpUrl, PurePath, RelativeFilePath],
) -> str:
    if isinstance(src, RelativeFilePath):
        return src.path.name
    elif isinstance(src, PurePath):
        return src.name
    else:
        url = urlparse(str(src))
        if (
            url.scheme == "https"
            and url.hostname == "zenodo.org"
            and url.path.startswith("/api/records/")
            and url.path.endswith("/content")
        ):
            return url.path.split("/")[-2]
        else:
            return url.path.split("/")[-1]


Sha256 = ValidatedString[
    Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, to_lower=True, min_length=64, max_length=64
        ),
    ]
]

R = TypeVar("R", HttpUrl, AbsoluteDirectory, pydantic.AnyUrl)


# TODO: Use RootModel?
class RelativePath:
    path: PurePosixPath
    absolute: Union[HttpUrl, AbsoluteDirectory, AbsoluteFilePath]
    """the absolute path (resolved at time of initialization with the root of the ValidationContext)"""

    def __init__(self, path: Union[str, Path, RelativePath]) -> None:
        super().__init__()
        if isinstance(path, RelativePath):
            self.path = path.path
            self.absolute = path.absolute
        else:
            if not isinstance(path, Path):
                path = Path(path)

            if path.is_absolute():
                raise ValueError(f"{path} is an absolute path")

            self.path = PurePosixPath(path.as_posix())
            root = validation_context_var.get().root
            if isinstance(root, HttpUrl):
                self.absolute = self.get_absolute(root)
            else:
                self.absolute = self.get_absolute(root)

    @property
    def __members(self):
        return (self.path,)

    def __eq__(self, __value: object) -> bool:
        return type(__value) is type(self) and self.__members == __value.__members

    def __hash__(self) -> int:
        return hash(self.__members)

    def __str__(self) -> str:
        return self.path.as_posix()

    def __repr__(self) -> str:
        return f"RelativePath('{self.path.as_posix()}')"

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ):
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    core_schema.is_instance_schema(pathlib.Path),
                    core_schema.str_schema(),
                ]
            ),
            serialization=core_schema.to_string_ser_schema(),
        )

    def get_absolute(self, root: R) -> R:
        if isinstance(root, pathlib.Path):
            return (root / self.path).absolute()

        parsed = urlsplit(str(root))
        path = list(parsed.path.strip("/").split("/"))
        rel_path = self.path.as_posix().strip("/")
        if (
            parsed.netloc == "zenodo.org"
            and parsed.path.startswith("/api/records/")
            and parsed.path.endswith("/content")
        ):
            path.insert(-1, rel_path)
        else:
            path.append(rel_path)

        url = urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                "/".join(path),
                parsed.query,
                parsed.fragment,
            )
        )
        if isinstance(root, pydantic.AnyUrl):
            return pydantic.AnyUrl(url)
        else:
            return HttpUrl(url)

    @classmethod
    def _validate(cls, value: Union[pathlib.Path, str]):
        if isinstance(value, str) and (
            value.startswith("https://") or value.startswith("http://")
        ):
            raise ValueError(f"{value} looks like a URL, not a relative path")

        ret = cls(value)
        if ret.path.is_absolute():
            raise ValueError(f"{value} is an absolute path.")

        return ret


class RelativeFilePath(RelativePath):
    absolute: Union[AbsoluteFilePath, HttpUrl]
    """the absolute file path (resolved at time of initialization with the root of the ValidationContext)"""

    @staticmethod
    def _exists_localy(path: pathlib.Path) -> None:
        if not path.is_file():
            raise ValueError(f"{path} does not point to an existing file")


class RelativeDirectory(RelativePath):
    absolute: Union[AbsoluteDirectory, HttpUrl]
    """the absolute directory (resolved at time of initialization with the root of the ValidationContext)"""

    @staticmethod
    def _exists_locally(path: pathlib.Path) -> None:
        if not path.is_dir():
            raise ValueError(f"{path} does not point to an existing directory")


FileSource = Union[HttpUrl, FilePath, RelativeFilePath, pydantic.HttpUrl]
PermissiveFileSource = Union[FileSource, str]

V_suffix = TypeVar("V_suffix", bound=FileSource)
path_or_url_adapter = TypeAdapter(Union[FilePath, DirectoryPath, HttpUrl])


def validate_suffix(value: V_suffix, *suffixes: str, case_sensitive: bool) -> V_suffix:
    """check final suffix"""
    assert len(suffixes) > 0, "no suffix given"
    assert all(
        suff.startswith(".") for suff in suffixes
    ), "expected suffixes to start with '.'"
    o_value = value
    strict = interprete_file_source(value)

    if isinstance(strict, (HttpUrl, AnyUrl)):
        if strict.path is None or "." not in (path := strict.path):
            suffix = ""
        elif (
            strict.host == "zenodo.org"
            and path.startswith("/api/records/")
            and path.endswith("/content")
        ):
            suffix = "." + path[: -len("/content")].split(".")[-1]
        else:
            suffix = "." + path.split(".")[-1]

    elif isinstance(strict, PurePath):
        suffix = strict.suffixes[-1]
    elif isinstance(strict, RelativeFilePath):
        suffix = strict.path.suffixes[-1]
    else:
        assert_never(strict)

    if (
        case_sensitive
        and suffix not in suffixes
        or not case_sensitive
        and suffix.lower() not in [s.lower() for s in suffixes]
    ):
        if len(suffixes) == 1:
            raise ValueError(f"Expected suffix {suffixes[0]}, but got {suffix}")
        else:
            raise ValueError(f"Expected a suffix from {suffixes}, but got {suffix}")

    return o_value


@dataclass(frozen=True, **SLOTS)
class WithSuffix:
    suffix: Union[LiteralString, Tuple[LiteralString, ...]]
    case_sensitive: bool

    def __get_pydantic_core_schema__(
        self, source: Type[Any], handler: GetCoreSchemaHandler
    ):
        if not self.suffix:
            raise ValueError("suffix may not be empty")

        schema = handler(source)
        if (
            schema["type"] != str
            and source != FileSource
            and not issubclass(source, (str, AnyUrl, RelativeFilePath, PurePath))
        ):
            raise TypeError("WithSuffix can only be applied to strings, URLs and paths")

        return core_schema.no_info_after_validator_function(
            self.validate,
            schema,
        )

    def validate(self, value: FileSource) -> FileSource:
        if isinstance(self.suffix, str):
            return validate_suffix(
                value, self.suffix, case_sensitive=self.case_sensitive
            )
        else:
            return validate_suffix(
                value, *self.suffix, case_sensitive=self.case_sensitive
            )


def _package(
    value: FileSource, handler: SerializerFunctionWrapHandler
) -> Union[FileSource, FileName]:
    from bioimageio.spec._internal.packaging_context import packaging_context_var

    ret = handler(value)

    if (packaging_context := packaging_context_var.get()) is None:
        return ret

    fsrcs = packaging_context.file_sources

    if isinstance(value, RelativeFilePath):
        src = value.absolute
    elif isinstance(value, (AnyUrl, HttpUrl)):
        src = value
    elif isinstance(value, Path):
        src = value.resolve()
    else:
        assert_never(value)

    fname = extract_file_name(src)
    assert not any(
        fname.endswith(special) for special in ALL_BIOIMAGEIO_YAML_NAMES
    ), fname
    if fname in fsrcs and fsrcs[fname] != src:
        for i in range(2, 20):
            fn, *ext = fname.split(".")
            alternative_file_name = ".".join([f"{fn}_{i}", *ext])
            if (
                alternative_file_name not in fsrcs
                or fsrcs[alternative_file_name] == src
            ):
                fname = alternative_file_name
                break
        else:
            raise RuntimeError(f"Too many file name clashes for {fname}")

    fsrcs[fname] = src
    return fname


def wo_special_file_name(src: FileSource) -> FileSource:
    if is_valid_rdf_name(src):
        raise ValueError(
            f"'{src}' not allowed here as its filename is reserved to identify"
            f" '{BIOIMAGEIO_YAML}' (or equivalent) files."
        )

    return src


IncludeInPackage: Callable[[], WrapSerializer] = partial(
    WrapSerializer, _package, when_used="unless-none"
)
ImportantFileSource = Annotated[
    FileSource, AfterValidator(wo_special_file_name), IncludeInPackage()
]


def is_valid_rdf_name(src: FileSource) -> bool:
    file_name = extract_file_name(src)
    for special in ALL_BIOIMAGEIO_YAML_NAMES:
        if file_name.endswith(special):
            return True

    return False


def ensure_is_valid_rdf_name(src: FileSource) -> FileSource:
    if not is_valid_rdf_name(src):
        raise ValueError(
            f"'{src}' does not have a valid filename to identify"
            f" '{BIOIMAGEIO_YAML}' (or equivalent) files."
        )

    return src


# types as loaded from YAML 1.2 (with ruyaml)
YamlLeafValue = Union[
    bool, _date, _datetime, int, float, str, None
]  # note: order relevant for deserializing
YamlKey = Union[  # YAML Arrays are cast to tuples if used as key in mappings
    YamlLeafValue, Tuple[YamlLeafValue, ...]  # (nesting is not allowed though)
]
YamlValue = _TypeAliasType(
    "YamlValue",
    Union[YamlLeafValue, List["YamlValue"], Dict[YamlKey, "YamlValue"]],
)
BioimageioYamlContent = Dict[str, YamlValue]
BioimageioYamlSource = Union[PermissiveFileSource, BioimageioYamlContent]


@dataclass
class OpenedBioimageioYaml:
    content: BioimageioYamlContent
    original_root: Union[Url, DirectoryPath]
    original_file_name: str


@dataclass
class DownloadedFile:
    path: FilePath
    original_root: Union[Url, DirectoryPath]
    original_file_name: str


class HashKwargs(TypedDict):
    sha256: NotRequired[Optional[str]]


StrictFileSource = Union[HttpUrl, FilePath, RelativeFilePath]
_strict_file_source_adapter = TypeAdapter(StrictFileSource)


def interprete_file_source(file_source: PermissiveFileSource) -> StrictFileSource:
    if isinstance(file_source, str):
        return _strict_file_source_adapter.validate_python(file_source)
    else:
        return file_source


def get_parent_url(url: Union[HttpUrl, pydantic.HttpUrl]) -> HttpUrl:
    parsed = urlsplit(str(url))
    path = list(parsed.path.split("/"))
    if (
        parsed.netloc == "zenodo.org"
        and parsed.path.startswith("/api/records/")
        and parsed.path.endswith("/content")
    ):
        path[-2:-1] = cast(List[str], [])
    else:
        path = path[:-1]

    return HttpUrl(
        urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                "/".join(path),
                parsed.query,
                parsed.fragment,
            )
        )
    )
