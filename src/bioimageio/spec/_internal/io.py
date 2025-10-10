from __future__ import annotations

import collections.abc
import hashlib
import sys
import warnings
import zipfile
from abc import abstractmethod
from contextlib import nullcontext
from dataclasses import dataclass, field
from datetime import date as _date
from datetime import datetime as _datetime
from functools import partial
from io import TextIOWrapper
from pathlib import Path, PurePath, PurePosixPath
from tempfile import mkdtemp
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
    overload,
)
from urllib.parse import urlparse, urlsplit, urlunsplit
from zipfile import ZipFile

import httpx
import pydantic
from genericache import NoopCache
from genericache.digest import ContentDigest, UrlDigest
from pydantic import (
    AnyUrl,
    DirectoryPath,
    Field,
    GetCoreSchemaHandler,
    PrivateAttr,
    RootModel,
    TypeAdapter,
    model_serializer,
    model_validator,
)
from pydantic_core import core_schema
from tqdm import tqdm
from typing_extensions import (
    Annotated,
    LiteralString,
    NotRequired,
    Self,
    TypeGuard,
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
    BytesReader,
    FileName,
    FilePath,
    Sha256,
    ZipPath,
    get_sha256,
)
from .node import Node
from .progress import Progressbar
from .root_url import RootHttpUrl
from .type_guards import is_dict, is_list, is_mapping, is_sequence
from .url import HttpUrl
from .utils import SLOTS
from .validation_context import get_validation_context

AbsolutePathT = TypeVar(
    "AbsolutePathT",
    bound=Union[HttpUrl, AbsoluteDirectory, AbsoluteFilePath, ZipPath],
)


class LightHttpFileDescr(Node):
    """http source with sha256 value (minimal validation)"""

    source: pydantic.HttpUrl
    """file source"""

    sha256: Sha256
    """SHA256 checksum of the source file"""

    def get_reader(
        self,
        *,
        progressbar: Union[Progressbar, Callable[[], Progressbar], bool, None] = None,
    ) -> BytesReader:
        """open the file source (download if needed)"""
        return get_reader(self.source, sha256=self.sha256, progressbar=progressbar)

    download = get_reader
    """alias for get_reader() method"""


class RelativePathBase(RootModel[PurePath], Generic[AbsolutePathT], frozen=True):
    _absolute: AbsolutePathT = PrivateAttr()

    @property
    def path(self) -> PurePath:
        return self.root

    def absolute(  # method not property analog to `pathlib.Path.absolute()`
        self,
    ) -> AbsolutePathT:
        """get the absolute path/url

        (resolved at time of initialization with the root of the ValidationContext)
        """
        return self._absolute

    def model_post_init(self, __context: Any) -> None:
        """set `_absolute` property with validation context at creation time. @private"""
        if self.root.is_absolute():
            raise ValueError(f"{self.root} is an absolute path.")

        if self.root.parts and self.root.parts[0] in ("http:", "https:"):
            raise ValueError(f"{self.root} looks like an http url.")

        self._absolute = (  # pyright: ignore[reportAttributeAccessIssue]
            self.get_absolute(get_validation_context().root)
        )
        super().model_post_init(__context)

    def __str__(self) -> str:
        return self.root.as_posix()

    def __repr__(self) -> str:
        return f"RelativePath('{self}')"

    @model_serializer()
    def format(self) -> str:
        return str(self)

    @abstractmethod
    def get_absolute(
        self, root: Union[RootHttpUrl, AbsoluteDirectory, pydantic.AnyUrl, ZipFile]
    ) -> AbsolutePathT: ...

    def _get_absolute_impl(
        self, root: Union[RootHttpUrl, AbsoluteDirectory, pydantic.AnyUrl, ZipFile]
    ) -> Union[Path, HttpUrl, ZipPath]:
        if isinstance(root, Path):
            return (root / self.root).absolute()

        rel_path = self.root.as_posix().strip("/")
        if isinstance(root, ZipFile):
            return ZipPath(root, rel_path)

        parsed = urlsplit(str(root))
        path = list(parsed.path.strip("/").split("/"))
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


class RelativeFilePath(
    RelativePathBase[Union[AbsoluteFilePath, HttpUrl, ZipPath]], frozen=True
):
    """A path relative to the `rdf.yaml` file (also if the RDF source is a URL)."""

    def model_post_init(self, __context: Any) -> None:
        """add validation @private"""
        if not self.root.parts:  # an empty path can only be a directory
            raise ValueError(f"{self.root} is not a valid file path.")

        super().model_post_init(__context)

    def get_absolute(
        self, root: "RootHttpUrl | Path | AnyUrl | ZipFile"
    ) -> "AbsoluteFilePath | HttpUrl | ZipPath":
        absolute = self._get_absolute_impl(root)
        if (
            isinstance(absolute, Path)
            and (context := get_validation_context()).perform_io_checks
            and str(self.root) not in context.known_files
            and not absolute.is_file()
        ):
            raise ValueError(f"{absolute} does not point to an existing file")

        return absolute


class RelativeDirectory(
    RelativePathBase[Union[AbsoluteDirectory, HttpUrl, ZipPath]], frozen=True
):
    def get_absolute(
        self, root: "RootHttpUrl | Path | AnyUrl | ZipFile"
    ) -> "AbsoluteDirectory | HttpUrl | ZipPath":
        absolute = self._get_absolute_impl(root)
        if (
            isinstance(absolute, Path)
            and get_validation_context().perform_io_checks
            and not absolute.is_dir()
        ):
            raise ValueError(f"{absolute} does not point to an existing directory")

        return absolute


FileSource = Annotated[
    Union[HttpUrl, RelativeFilePath, FilePath],
    Field(union_mode="left_to_right"),
]
PermissiveFileSource = Union[FileSource, str, pydantic.HttpUrl]


class FileDescr(Node):
    """A file description"""

    source: FileSource
    """File source"""

    sha256: Optional[Sha256] = None
    """SHA256 hash value of the **source** file."""

    @model_validator(mode="after")
    def _validate_sha256(self) -> Self:
        if get_validation_context().perform_io_checks:
            self.validate_sha256()

        return self

    def validate_sha256(self, force_recompute: bool = False) -> None:
        """validate the sha256 hash value of the **source** file"""
        context = get_validation_context()
        src_str = str(self.source)
        if not force_recompute and src_str in context.known_files:
            actual_sha = context.known_files[src_str]
        else:
            reader = get_reader(self.source, sha256=self.sha256)
            if force_recompute:
                actual_sha = get_sha256(reader)
            else:
                actual_sha = reader.sha256

            context.known_files[src_str] = actual_sha

        if actual_sha is None:
            return
        elif self.sha256 == actual_sha:
            pass
        elif self.sha256 is None or context.update_hashes:
            self.sha256 = actual_sha
        elif self.sha256 != actual_sha:
            raise ValueError(
                f"Sha256 mismatch for {self.source}. Expected {self.sha256}, got "
                + f"{actual_sha}. Update expected `sha256` or point to the matching "
                + "file."
            )

    def get_reader(
        self,
        *,
        progressbar: Union[Progressbar, Callable[[], Progressbar], bool, None] = None,
    ):
        """open the file source (download if needed)"""
        return get_reader(self.source, progressbar=progressbar, sha256=self.sha256)

    download = get_reader
    """alias for get_reader() method"""


path_or_url_adapter: "TypeAdapter[Union[FilePath, DirectoryPath, HttpUrl]]" = (
    TypeAdapter(Union[FilePath, DirectoryPath, HttpUrl])
)


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

    def validate(
        self, value: Union[FileSource, FileDescr]
    ) -> Union[FileSource, FileDescr]:
        return validate_suffix(value, self.suffix, case_sensitive=self.case_sensitive)


def wo_special_file_name(src: F) -> F:
    if has_valid_bioimageio_yaml_name(src):
        raise ValueError(
            f"'{src}' not allowed here as its filename is reserved to identify"
            + f" '{BIOIMAGEIO_YAML}' (or equivalent) files."
        )

    return src


def has_valid_bioimageio_yaml_name(src: Union[FileSource, FileDescr]) -> bool:
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


def find_bioimageio_yaml_file_name(path: Union[Path, ZipFile]) -> FileName:
    if isinstance(path, ZipFile):
        file_names = path.namelist()
    elif path.is_file():
        if not zipfile.is_zipfile(path):
            return path.name

        with ZipFile(path, "r") as f:
            file_names = f.namelist()
    else:
        file_names = [p.name for p in path.glob("*")]

    return identify_bioimageio_yaml_file_name(
        file_names
    )  # TODO: try/except with better error message for dir


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
if TYPE_CHECKING:
    YamlValue = Union[YamlLeafValue, List["YamlValue"], Dict[YamlKey, "YamlValue"]]
    YamlValueView = Union[
        YamlLeafValue, Sequence["YamlValueView"], Mapping[YamlKey, "YamlValueView"]
    ]
else:
    # for pydantic validation we need to use `TypeAliasType`,
    # see https://docs.pydantic.dev/latest/concepts/types/#named-recursive-types
    # however this results in a partially unknown type with the current pyright 1.1.388
    YamlValue = _TypeAliasType(
        "YamlValue",
        Union[YamlLeafValue, List["YamlValue"], Dict[YamlKey, "YamlValue"]],
    )
    YamlValueView = _TypeAliasType(
        "YamlValueView",
        Union[
            YamlLeafValue,
            Sequence["YamlValueView"],
            Mapping[YamlKey, "YamlValueView"],
        ],
    )

BioimageioYamlContent = Dict[str, YamlValue]
BioimageioYamlContentView = Mapping[str, YamlValueView]
BioimageioYamlSource = Union[
    PermissiveFileSource, ZipFile, BioimageioYamlContent, BioimageioYamlContentView
]


@overload
def deepcopy_yaml_value(value: BioimageioYamlContentView) -> BioimageioYamlContent: ...


@overload
def deepcopy_yaml_value(value: YamlValueView) -> YamlValue: ...


def deepcopy_yaml_value(
    value: Union[BioimageioYamlContentView, YamlValueView],
) -> Union[BioimageioYamlContent, YamlValue]:
    if isinstance(value, str):
        return value
    elif isinstance(value, collections.abc.Mapping):
        return {key: deepcopy_yaml_value(val) for key, val in value.items()}
    elif isinstance(value, collections.abc.Sequence):
        return [deepcopy_yaml_value(val) for val in value]
    else:
        return value


def is_yaml_leaf_value(value: Any) -> TypeGuard[YamlLeafValue]:
    return isinstance(value, (bool, _date, _datetime, int, float, str, type(None)))


def is_yaml_list(value: Any) -> TypeGuard[List[YamlValue]]:
    return is_list(value) and all(is_yaml_value(item) for item in value)


def is_yaml_sequence(value: Any) -> TypeGuard[List[YamlValueView]]:
    return is_sequence(value) and all(is_yaml_value(item) for item in value)


def is_yaml_dict(value: Any) -> TypeGuard[BioimageioYamlContent]:
    return is_dict(value) and all(
        isinstance(key, str) and is_yaml_value(val) for key, val in value.items()
    )


def is_yaml_mapping(value: Any) -> TypeGuard[BioimageioYamlContentView]:
    return is_mapping(value) and all(
        isinstance(key, str) and is_yaml_value_read_only(val)
        for key, val in value.items()
    )


def is_yaml_value(value: Any) -> TypeGuard[YamlValue]:
    return is_yaml_leaf_value(value) or is_yaml_list(value) or is_yaml_dict(value)


def is_yaml_value_read_only(value: Any) -> TypeGuard[YamlValueView]:
    return (
        is_yaml_leaf_value(value) or is_yaml_sequence(value) or is_yaml_mapping(value)
    )


@dataclass(frozen=True, **SLOTS)
class OpenedBioimageioYaml:
    content: BioimageioYamlContent = field(repr=False)
    original_root: Union[AbsoluteDirectory, RootHttpUrl, ZipFile]
    original_source_name: Optional[str]
    original_file_name: FileName
    unparsed_content: str = field(repr=False)


@dataclass(frozen=True, **SLOTS)
class LocalFile:
    path: FilePath
    original_root: Union[AbsoluteDirectory, RootHttpUrl, ZipFile]
    original_file_name: FileName


@dataclass(frozen=True, **SLOTS)
class FileInZip:
    path: ZipPath
    original_root: Union[RootHttpUrl, ZipFile]
    original_file_name: FileName


class HashKwargs(TypedDict):
    sha256: NotRequired[Optional[Sha256]]


_file_source_adapter: TypeAdapter[Union[HttpUrl, RelativeFilePath, FilePath]] = (
    TypeAdapter(FileSource)
)


def interprete_file_source(file_source: PermissiveFileSource) -> FileSource:
    if isinstance(file_source, Path):
        if file_source.is_dir():
            raise FileNotFoundError(
                f"{file_source} is a directory, but expected a file."
            )
        return file_source

    if isinstance(file_source, HttpUrl):
        return file_source

    if isinstance(file_source, pydantic.AnyUrl):
        file_source = str(file_source)

    with get_validation_context().replace(perform_io_checks=False):
        strict = _file_source_adapter.validate_python(file_source)
        if isinstance(strict, Path) and strict.is_dir():
            raise FileNotFoundError(f"{strict} is a directory, but expected a file.")

    return strict


def extract(
    source: Union[FilePath, ZipFile, ZipPath],
    folder: Optional[DirectoryPath] = None,
    overwrite: bool = False,
) -> DirectoryPath:
    extract_member = None
    if isinstance(source, ZipPath):
        extract_member = source.at
        source = source.root

    if isinstance(source, ZipFile):
        zip_context = nullcontext(source)
        if folder is None:
            if source.filename is None:
                folder = Path(mkdtemp())
            else:
                zip_path = Path(source.filename)
                folder = zip_path.with_suffix(zip_path.suffix + ".unzip")
    else:
        zip_context = ZipFile(source, "r")
        if folder is None:
            folder = source.with_suffix(source.suffix + ".unzip")

    if overwrite and folder.exists():
        warnings.warn(f"Overwriting existing unzipped archive at {folder}")

    with zip_context as f:
        if extract_member is not None:
            extracted_file_path = folder / extract_member
            if extracted_file_path.exists() and not overwrite:
                warnings.warn(f"Found unzipped {extracted_file_path}.")
            else:
                _ = f.extract(extract_member, folder)

            return folder

        elif overwrite or not folder.exists():
            f.extractall(folder)
            return folder

        found_content = {p.relative_to(folder).as_posix() for p in folder.glob("*")}
        expected_content = {info.filename for info in f.filelist}
        if expected_missing := expected_content - found_content:
            parts = folder.name.split("_")
            nr, *suffixes = parts[-1].split(".")
            if nr.isdecimal():
                nr = str(int(nr) + 1)
            else:
                nr = f"1.{nr}"

            parts[-1] = ".".join([nr, *suffixes])
            out_path_new = folder.with_name("_".join(parts))
            warnings.warn(
                f"Unzipped archive at {folder} is missing expected files"
                + f" {expected_missing}."
                + f" Unzipping to {out_path_new} instead to avoid overwriting."
            )
            return extract(f, out_path_new, overwrite=overwrite)
        else:
            warnings.warn(
                f"Found unzipped archive with all expected files at {folder}."
            )
            return folder


def get_reader(
    source: Union[PermissiveFileSource, FileDescr, ZipPath],
    /,
    progressbar: Union[Progressbar, Callable[[], Progressbar], bool, None] = None,
    **kwargs: Unpack[HashKwargs],
) -> BytesReader:
    """Open a file `source` (download if needed)"""
    if isinstance(source, FileDescr):
        if "sha256" not in kwargs:
            kwargs["sha256"] = source.sha256

        source = source.source
    elif isinstance(source, str):
        source = interprete_file_source(source)

    if isinstance(source, RelativeFilePath):
        source = source.absolute()
    elif isinstance(source, pydantic.AnyUrl):
        with get_validation_context().replace(perform_io_checks=False):
            source = HttpUrl(source)

    if isinstance(source, HttpUrl):
        return _open_url(source, progressbar=progressbar, **kwargs)

    if isinstance(source, ZipPath):
        if not source.exists():
            raise FileNotFoundError(source)

        f = source.open(mode="rb")
        assert not isinstance(f, TextIOWrapper)
        root = source.root
    elif isinstance(source, Path):
        if source.is_dir():
            raise FileNotFoundError(f"{source} is a directory, not a file")

        if not source.exists():
            raise FileNotFoundError(source)

        f = source.open("rb")
        root = source.parent
    else:
        assert_never(source)

    expected_sha = kwargs.get("sha256")
    if expected_sha is None:
        sha = None
    else:
        sha = get_sha256(f)
        _ = f.seek(0)
        if sha != expected_sha:
            raise ValueError(
                f"SHA256 mismatch for {source}. Expected {expected_sha}, got {sha}."
            )

    return BytesReader(
        f,
        sha256=sha,
        suffix=source.suffix,
        original_file_name=source.name,
        original_root=root,
        is_zipfile=None,
    )


download = get_reader


def _open_url(
    source: HttpUrl,
    /,
    progressbar: Union[Progressbar, Callable[[], Progressbar], bool, None],
    **kwargs: Unpack[HashKwargs],
) -> BytesReader:
    cache = (
        NoopCache[RootHttpUrl](url_hasher=UrlDigest.from_str)
        if get_validation_context().disable_cache
        else settings.disk_cache
    )
    sha = kwargs.get("sha256")
    digest = False if sha is None else ContentDigest.parse(hexdigest=sha)
    source_path = PurePosixPath(
        source.path
        or sha
        or hashlib.sha256(str(source).encode(encoding="utf-8")).hexdigest()
    )

    reader = cache.fetch(
        source,
        fetcher=partial(_fetch_url, progressbar=progressbar),
        force_refetch=digest,
    )
    return BytesReader(
        reader,
        suffix=source_path.suffix,
        sha256=sha,
        original_file_name=source_path.name,
        original_root=source.parent,
        is_zipfile=None,
    )


def _fetch_url(
    source: RootHttpUrl,
    *,
    progressbar: Union[Progressbar, Callable[[], Progressbar], bool, None],
):
    if source.scheme not in ("http", "https"):
        raise NotImplementedError(source.scheme)

    if progressbar is None:
        # chose progressbar option from validation context
        progressbar = get_validation_context().progressbar

    if progressbar is None:
        # default to no progressbar in CI environments
        progressbar = not settings.CI

    if callable(progressbar):
        progressbar = progressbar()

    if isinstance(progressbar, bool) and progressbar:
        progressbar = tqdm(
            ncols=79,
            ascii=bool(sys.platform == "win32"),
            unit="B",
            unit_scale=True,
            leave=True,
        )

    if progressbar is not False:
        progressbar.set_description(f"Downloading {extract_file_name(source)}")

    headers: Dict[str, str] = {}
    if settings.user_agent is not None:
        headers["User-Agent"] = settings.user_agent
    elif settings.CI:
        headers["User-Agent"] = "ci"

    r = httpx.get(
        str(source),
        follow_redirects=True,
        headers=headers,
        timeout=settings.http_timeout,
    )
    _ = r.raise_for_status()

    # set progressbar.total
    total = r.headers.get("content-length")
    if total is not None and not isinstance(total, int):
        try:
            total = int(total)
        except Exception:
            total = None

    if progressbar is not False:
        if total is None:
            progressbar.total = 0
        else:
            progressbar.total = total

    def iter_content():
        for chunk in r.iter_bytes(chunk_size=4096):
            yield chunk
            if progressbar is not False:
                _ = progressbar.update(len(chunk))

        # Make sure the progress bar gets filled even if the actual number
        # is chunks is smaller than expected. This happens when streaming
        # text files that are compressed by the server when sending (gzip).
        # Binary files don't experience this.
        # (adapted from pooch.HttpDownloader)
        if progressbar is not False:
            progressbar.reset()
            if total is not None:
                _ = progressbar.update(total)

            progressbar.close()

    return iter_content()


def extract_file_name(
    src: Union[
        pydantic.HttpUrl, RootHttpUrl, PurePath, RelativeFilePath, ZipPath, FileDescr
    ],
) -> FileName:
    if isinstance(src, FileDescr):
        src = src.source

    if isinstance(src, ZipPath):
        return src.name or src.root.filename or "bioimageio.zip"
    elif isinstance(src, RelativeFilePath):
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


def extract_file_descrs(data: YamlValueView):
    collected: List[FileDescr] = []
    with get_validation_context().replace(perform_io_checks=False, log_warnings=False):
        _extract_file_descrs_impl(data, collected)

    return collected


def _extract_file_descrs_impl(data: YamlValueView, collected: List[FileDescr]):
    if isinstance(data, collections.abc.Mapping):
        if "source" in data and "sha256" in data:
            try:
                fd = FileDescr.model_validate(
                    dict(source=data["source"], sha256=data["sha256"])
                )
            except Exception:
                pass
            else:
                collected.append(fd)

        for v in data.values():
            _extract_file_descrs_impl(v, collected)
    elif not isinstance(data, str) and isinstance(data, collections.abc.Sequence):
        for v in data:
            _extract_file_descrs_impl(v, collected)


F = TypeVar("F", bound=Union[FileSource, FileDescr])


def validate_suffix(
    value: F, suffix: Union[str, Sequence[str]], case_sensitive: bool
) -> F:
    """check final suffix"""
    if isinstance(suffix, str):
        suffixes = [suffix]
    else:
        suffixes = suffix

    assert len(suffixes) > 0, "no suffix given"
    assert all(suff.startswith(".") for suff in suffixes), (
        "expected suffixes to start with '.'"
    )
    o_value = value
    if isinstance(value, FileDescr):
        strict = value.source
    else:
        strict = interprete_file_source(value)

    if isinstance(strict, (HttpUrl, AnyUrl)):
        if strict.path is None or "." not in (path := strict.path):
            actual_suffixes = []
        else:
            if (
                strict.host == "zenodo.org"
                and path.startswith("/api/records/")
                and path.endswith("/content")
            ):
                # Zenodo API URLs have a "/content" suffix that should be ignored
                path = path[: -len("/content")]

            actual_suffixes = [f".{path.split('.')[-1]}"]

    elif isinstance(strict, PurePath):
        actual_suffixes = strict.suffixes
    elif isinstance(strict, RelativeFilePath):
        actual_suffixes = strict.path.suffixes
    else:
        assert_never(strict)

    if actual_suffixes:
        actual_suffix = actual_suffixes[-1]
    else:
        actual_suffix = "no suffix"

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


def populate_cache(sources: Sequence[Union[FileDescr, LightHttpFileDescr]]):
    unique: Set[str] = set()
    for src in sources:
        if src.sha256 is None:
            continue  # not caching without known SHA

        if isinstance(src.source, (HttpUrl, pydantic.AnyUrl)):
            url = str(src.source)
        elif isinstance(src.source, RelativeFilePath):
            if isinstance(absolute := src.source.absolute(), HttpUrl):
                url = str(absolute)
            else:
                continue  # not caching local paths
        elif isinstance(src.source, Path):
            continue  # not caching local paths
        else:
            assert_never(src.source)

        if url in unique:
            continue  # skip duplicate URLs

        unique.add(url)
        _ = src.download()
