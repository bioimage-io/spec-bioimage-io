from __future__ import annotations

import hashlib
import sys
import warnings
from abc import abstractmethod
from dataclasses import dataclass
from datetime import date as _date
from datetime import datetime as _datetime
from functools import lru_cache
from pathlib import Path, PurePath
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
)
from urllib.parse import urlparse, urlsplit, urlunsplit
from zipfile import ZipFile, is_zipfile

import pooch
import pydantic
from pydantic import (
    AnyUrl,
    DirectoryPath,
    Field,
    FilePath,
    GetCoreSchemaHandler,
    PlainSerializer,
    PrivateAttr,
    RootModel,
    SerializationInfo,
    TypeAdapter,
    model_validator,
)
from pydantic_core import core_schema
from typing_extensions import (
    Annotated,
    LiteralString,
    NotRequired,
    Self,
    Unpack,
    assert_never,
)
from typing_extensions import TypeAliasType as _TypeAliasType

from ._settings import settings
from .io_basics import (
    ALL_BIOIMAGEIO_YAML_NAMES,
    ALTERNATIVE_BIOIMAGEIO_YAML_NAMES,
    BIOIMAGEIO_YAML,
    AbsoluteDirectory,
    AbsoluteFilePath,
    FileName,
    Sha256,
)
from .node import Node
from .packaging_context import packaging_context_var
from .root_url import RootHttpUrl
from .url import HttpUrl
from .validation_context import validation_context_var
from .validator_annotations import AfterValidator

if sys.version_info < (3, 10):
    SLOTS: Dict[str, bool] = {}
else:
    SLOTS = {"slots": True}


AbsolutePathT = TypeVar(
    "AbsolutePathT", bound=Union[HttpUrl, AbsoluteDirectory, AbsoluteFilePath]
)


class RelativePathBase(RootModel[PurePath], Generic[AbsolutePathT], frozen=True):
    _absolute: AbsolutePathT = PrivateAttr()

    @property
    def path(self) -> PurePath:
        return self.root

    @property
    def absolute(self) -> AbsolutePathT:
        """the absolute path/url (resolved at time of initialization with the root of the ValidationContext)"""
        return self._absolute

    def model_post_init(self, __context: Any) -> None:
        if self.root.is_absolute():
            raise ValueError(f"{self.root} is an absolute path.")

        if self.root.parts and self.root.parts[0] in ("http:", "https:"):
            raise ValueError(f"{self.root} looks like an http url.")

        self._absolute = (  # pyright: ignore[reportAttributeAccessIssue]
            self.get_absolute(validation_context_var.get().root)
        )
        super().model_post_init(__context)

    # @property
    # def __members(self):
    #     return (self.path,)

    # def __eq__(self, __value: object) -> bool:
    #     return type(__value) is type(self) and self.__members == __value.__members

    # def __hash__(self) -> int:
    #     return hash(self.__members)

    def __str__(self) -> str:
        return self.root.as_posix()

    def __repr__(self) -> str:
        return f"RelativePath('{self}')"

    @abstractmethod
    def get_absolute(
        self, root: Union[RootHttpUrl, AbsoluteDirectory, pydantic.AnyUrl]
    ) -> AbsolutePathT: ...

    def _get_absolute_impl(
        self, root: Union[RootHttpUrl, AbsoluteDirectory, pydantic.AnyUrl]
    ) -> Union[Path, HttpUrl]:
        if isinstance(root, Path):
            return (root / self.root).absolute()

        parsed = urlsplit(str(root))
        path = list(parsed.path.strip("/").split("/"))
        rel_path = self.root.as_posix().strip("/")
        if (
            parsed.netloc == "zenodo.org"
            and parsed.path.startswith("/api/records/")
            and parsed.path.endswith("/content")
        ):
            path.insert(-1, rel_path)
        else:
            path.append(rel_path)

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

    @classmethod
    def _validate(cls, value: Union[PurePath, str]):
        if isinstance(value, str) and (
            value.startswith("https://") or value.startswith("http://")
        ):
            raise ValueError(f"{value} looks like a URL, not a relative path")

        return cls(PurePath(value))


class RelativePath(
    RelativePathBase[Union[AbsoluteFilePath, AbsoluteDirectory, HttpUrl]], frozen=True
):
    def get_absolute(
        self, root: "RootHttpUrl | Path | AnyUrl"
    ) -> "AbsoluteFilePath | AbsoluteDirectory | HttpUrl":
        absolute = self._get_absolute_impl(root)
        if (
            isinstance(absolute, Path)
            and (context := validation_context_var.get()).perform_io_checks
            and str(self.root) not in context.known_files
            and not absolute.exists()
        ):
            raise ValueError(f"{absolute} does not exist")

        return absolute


class RelativeFilePath(RelativePathBase[Union[AbsoluteFilePath, HttpUrl]], frozen=True):
    def model_post_init(self, __context: Any) -> None:
        if not self.root.parts:  # an empty path can only be a directory
            raise ValueError(f"{self.root} is not a valid file path.")

        super().model_post_init(__context)

    def get_absolute(
        self, root: "RootHttpUrl | Path | AnyUrl"
    ) -> "AbsoluteFilePath | HttpUrl":
        absolute = self._get_absolute_impl(root)
        if (
            isinstance(absolute, Path)
            and (context := validation_context_var.get()).perform_io_checks
            and str(self.root) not in context.known_files
            and not absolute.is_file()
        ):
            raise ValueError(f"{absolute} does not point to an existing file")

        return absolute


class RelativeDirectory(
    RelativePathBase[Union[AbsoluteDirectory, HttpUrl]], frozen=True
):
    def get_absolute(
        self, root: "RootHttpUrl | Path | AnyUrl"
    ) -> "AbsoluteDirectory | HttpUrl":
        absolute = self._get_absolute_impl(root)
        if (
            isinstance(absolute, Path)
            and validation_context_var.get().perform_io_checks
            and not absolute.is_dir()
        ):
            raise ValueError(f"{absolute} does not point to an existing directory")

        return absolute


FileSource = Annotated[
    Union[FilePath, HttpUrl, RelativeFilePath, pydantic.HttpUrl],
    Field(union_mode="left_to_right"),
]
PermissiveFileSource = Union[FileSource, str]

V_suffix = TypeVar("V_suffix", bound=FileSource)
path_or_url_adapter = TypeAdapter(Union[FilePath, DirectoryPath, HttpUrl])


def validate_suffix(
    value: V_suffix, suffix: Union[str, Sequence[str]], case_sensitive: bool
) -> V_suffix:
    """check final suffix"""
    if isinstance(suffix, str):
        suffixes = [suffix]
    else:
        suffixes = suffix

    assert len(suffixes) > 0, "no suffix given"
    assert all(
        suff.startswith(".") for suff in suffixes
    ), "expected suffixes to start with '.'"
    o_value = value
    strict = interprete_file_source(value)

    if isinstance(strict, (HttpUrl, AnyUrl)):
        if strict.path is None or "." not in (path := strict.path):
            actual_suffix = ""
        elif (
            strict.host == "zenodo.org"
            and path.startswith("/api/records/")
            and path.endswith("/content")
        ):
            actual_suffix = "." + path[: -len("/content")].split(".")[-1]
        else:
            actual_suffix = "." + path.split(".")[-1]

    elif isinstance(strict, PurePath):
        actual_suffix = strict.suffixes[-1]
    elif isinstance(strict, RelativeFilePath):
        actual_suffix = strict.path.suffixes[-1]
    else:
        assert_never(strict)

    if (
        case_sensitive
        and actual_suffix not in suffixes
        or not case_sensitive
        and actual_suffix.lower() not in [s.lower() for s in suffixes]
    ):
        if len(suffixes) == 1:
            raise ValueError(f"Expected suffix {suffixes[0]}, but got {actual_suffix}")
        else:
            raise ValueError(
                f"Expected a suffix from {suffixes}, but got {actual_suffix}"
            )

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
        return core_schema.no_info_after_validator_function(
            self.validate,
            schema,
        )

    def validate(self, value: FileSource) -> FileSource:
        return validate_suffix(value, self.suffix, case_sensitive=self.case_sensitive)


def wo_special_file_name(src: FileSource) -> FileSource:
    if has_valid_bioimageio_yaml_name(src):
        raise ValueError(
            f"'{src}' not allowed here as its filename is reserved to identify"
            + f" '{BIOIMAGEIO_YAML}' (or equivalent) files."
        )

    return src


def _package(value: FileSource, info: SerializationInfo) -> Union[str, Path, FileName]:
    if (packaging_context := packaging_context_var.get()) is None:
        # convert to standard python obj
        # note: pydantic keeps returning Rootmodels (here `HttpUrl`) as-is, but if
        #   this function returns one RootModel, paths are "further serialized" by
        #   returning the 'root' attribute, which is incorrect.
        #   see https://github.com/pydantic/pydantic/issues/8963
        #   TODO: follow up on https://github.com/pydantic/pydantic/issues/8963
        if isinstance(value, Path):
            unpackaged = value
        elif isinstance(value, HttpUrl):
            unpackaged = value
        elif isinstance(value, RelativeFilePath):
            unpackaged = Path(value.path)
        elif isinstance(value, AnyUrl):
            unpackaged = str(value)
        else:
            assert_never(value)

        if info.mode_is_json():
            # convert to json value  # TODO: remove and let pydantic do this?
            if isinstance(unpackaged, Path):
                unpackaged = str(unpackaged)
            elif isinstance(unpackaged, str):
                pass
            else:
                assert_never(unpackaged)
        else:
            warnings.warn(
                "dumping with mode='python' is currently not fully supported for "
                + "fields that are included when packaging; returned objects are "
                + "standard python objects"
            )

        return unpackaged  # return unpackaged file source

    # package the file source:
    # add it to the current package's file sources and return its collision free file name
    if isinstance(value, RelativeFilePath):
        src = value.absolute
    elif isinstance(value, pydantic.AnyUrl):
        src = HttpUrl(str(value))
    elif isinstance(value, HttpUrl):
        src = value
    elif isinstance(value, Path):
        src = value.resolve()
    else:
        assert_never(value)

    fname = extract_file_name(src)
    if fname == packaging_context.bioimageio_yaml_file_name:
        raise ValueError(
            f"Reserved file name '{packaging_context.bioimageio_yaml_file_name}' "
            + "not allowed for a file to be packaged"
        )

    fsrcs = packaging_context.file_sources
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
            raise ValueError(f"Too many file name clashes for {fname}")

    fsrcs[fname] = src
    return fname


include_in_package_serializer = PlainSerializer(_package, when_used="unless-none")
ImportantFileSource = Annotated[
    FileSource,
    AfterValidator(wo_special_file_name),
    include_in_package_serializer,
]
InPackageIfLocalFileSource = Union[
    Annotated[
        Union[FilePath, RelativeFilePath],
        AfterValidator(wo_special_file_name),
        include_in_package_serializer,
    ],
    Union[HttpUrl, pydantic.HttpUrl],
]


def has_valid_bioimageio_yaml_name(src: FileSource) -> bool:
    return is_valid_bioimageio_yaml_name(extract_file_name(src))


def is_valid_bioimageio_yaml_name(file_name: FileName) -> bool:
    for bioimageio_name in ALL_BIOIMAGEIO_YAML_NAMES:
        if file_name == bioimageio_name or file_name.endswith("." + bioimageio_name):
            return True

    return False


def identify_bioimageio_yaml_file_name(file_names: Iterable[FileName]) -> FileName:
    file_names = sorted(file_names)
    for bioimageio_name in ALL_BIOIMAGEIO_YAML_NAMES:
        for file_name in file_names:
            if file_name == bioimageio_name or file_name.endswith(
                "." + bioimageio_name
            ):
                return file_name

    raise ValueError(
        f"No {BIOIMAGEIO_YAML} found in {file_names}. (Looking for '{BIOIMAGEIO_YAML}'"
        + " or or any of the alterntive file names:"
        + f" {ALTERNATIVE_BIOIMAGEIO_YAML_NAMES}, or any file with an extension of"
        + f"  those, e.g. 'anything.{BIOIMAGEIO_YAML}')."
    )


def find_bioimageio_yaml_file_name(path: Path) -> FileName:
    if path.is_file():
        if not is_zipfile(path):
            return path.name

        with ZipFile(path, "r") as f:
            file_names = identify_bioimageio_yaml_file_name(f.namelist())
    else:
        file_names = [p.name for p in path.glob("*")]

    return identify_bioimageio_yaml_file_name(file_names)


def ensure_has_valid_bioimageio_yaml_name(src: FileSource) -> FileSource:
    if not has_valid_bioimageio_yaml_name(src):
        raise ValueError(
            f"'{src}' does not have a valid filename to identify"
            + f" '{BIOIMAGEIO_YAML}' (or equivalent) files."
        )

    return src


def ensure_is_valid_bioimageio_yaml_name(file_name: FileName) -> FileName:
    if not is_valid_bioimageio_yaml_name(file_name):
        raise ValueError(
            f"'{file_name}' is not a valid filename to identify"
            + f" '{BIOIMAGEIO_YAML}' (or equivalent) files."
        )

    return file_name


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
    original_root: Union[AbsoluteDirectory, RootHttpUrl]
    original_file_name: FileName


@dataclass
class DownloadedFile:
    path: FilePath
    original_root: Union[AbsoluteDirectory, RootHttpUrl]
    original_file_name: FileName


class HashKwargs(TypedDict):
    sha256: NotRequired[Optional[Sha256]]


StrictFileSource = Annotated[
    Union[HttpUrl, FilePath, RelativeFilePath], Field(union_mode="left_to_right")
]
_strict_file_source_adapter = TypeAdapter(StrictFileSource)


def interprete_file_source(file_source: PermissiveFileSource) -> StrictFileSource:
    if isinstance(file_source, (HttpUrl, Path)):
        return file_source

    if isinstance(file_source, pydantic.AnyUrl):
        file_source = str(file_source)

    with validation_context_var.get().replace(perform_io_checks=False):
        strict = _strict_file_source_adapter.validate_python(file_source)

    return strict


def _get_known_hash(hash_kwargs: HashKwargs):
    if "sha256" in hash_kwargs and hash_kwargs["sha256"] is not None:
        return f"sha256:{hash_kwargs['sha256']}"
    else:
        return None


def _get_unique_file_name(url: Union[HttpUrl, pydantic.HttpUrl]):
    """
    Create a unique file name based on the given URL;
    adapted from pooch.utils.unique_file_name
    """
    md5 = hashlib.md5(str(url).encode()).hexdigest()
    fname = extract_file_name(url)
    # Crop the start of the file name to fit 255 characters including the hash
    # and the :
    fname = fname[-(255 - len(md5) - 1) :]
    unique_name = f"{md5}-{fname}"
    return unique_name


def download(
    source: Union[PermissiveFileSource, FileDescr],
    /,
    **kwargs: Unpack[HashKwargs],
) -> DownloadedFile:
    """download `source` URL (or pass local file path)"""
    if isinstance(source, FileDescr):
        return source.download()

    strict_source = interprete_file_source(source)
    if isinstance(strict_source, RelativeFilePath):
        strict_source = strict_source.absolute

    if isinstance(strict_source, PurePath):
        if not strict_source.exists():
            raise FileNotFoundError(strict_source)
        local_source = strict_source
        root: Union[RootHttpUrl, DirectoryPath] = strict_source.parent
    else:
        if strict_source.scheme not in ("http", "https"):
            raise NotImplementedError(strict_source.scheme)

        if settings.CI:
            headers = {"User-Agent": "ci"}
            progressbar = False
        else:
            headers = {}
            progressbar = True

        if settings.user_agent is not None:
            headers["User-Agent"] = settings.user_agent

        downloader = pooch.HTTPDownloader(headers=headers, progressbar=progressbar)
        fname = _get_unique_file_name(strict_source)
        _ls: Any = pooch.retrieve(
            url=str(strict_source),
            known_hash=_get_known_hash(kwargs),
            downloader=downloader,
            fname=fname,
            path=settings.cache_path,
        )
        local_source = Path(_ls).absolute()
        root = strict_source.parent

    return DownloadedFile(
        local_source,
        root,
        extract_file_name(strict_source),
    )


class FileDescr(Node):
    source: ImportantFileSource
    """∈📦 file source"""

    sha256: Optional[Sha256] = None
    """SHA256 checksum of the source file"""

    @model_validator(mode="after")
    def validate_sha256(self) -> Self:
        context = validation_context_var.get()
        if not context.perform_io_checks:
            return self
        elif (src_str := str(self.source)) in context.known_files:
            actual_sha = context.known_files[src_str]
        else:
            local_source = download(self.source, sha256=self.sha256).path
            actual_sha = get_sha256(local_source)
            context.known_files[str(self.source)] = actual_sha

        if self.sha256 is None:
            self.sha256 = actual_sha
        elif self.sha256 != actual_sha:
            raise ValueError(
                f"Sha256 mismatch for {self.source}. Expected {self.sha256}, got "
                + f"{actual_sha}. Update expected `sha256` or point to the matching "
                + "file."
            )

        return self

    def download(self):

        return download(self.source, sha256=self.sha256)


def extract_file_name(
    src: Union[pydantic.HttpUrl, HttpUrl, PurePath, RelativeFilePath],
) -> FileName:
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


@lru_cache
def get_sha256(path: Path) -> Sha256:
    """from https://stackoverflow.com/a/44873382"""
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(path, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])

    sha = h.hexdigest()
    assert len(sha) == 64
    return Sha256(sha)
