from __future__ import annotations

import hashlib
import sys
import warnings
from abc import abstractmethod
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import date as _date
from datetime import datetime as _datetime
from functools import lru_cache
from pathlib import Path, PurePath
from tempfile import mktemp
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
)
from urllib.parse import urlparse, urlsplit, urlunsplit
from zipfile import ZipFile, is_zipfile

import pooch  # pyright: ignore [reportMissingTypeStubs]
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
    FileName,
    Sha256,
    ZipPath,
)
from .node import Node
from .packaging_context import packaging_context_var
from .root_url import RootHttpUrl
from .type_guards import is_mapping, is_sequence
from .url import HttpUrl
from .validation_context import validation_context_var
from .validator_annotations import AfterValidator

if sys.version_info < (3, 10):
    SLOTS: Dict[str, bool] = {}
else:
    SLOTS = {"slots": True}


AbsolutePathT = TypeVar(
    "AbsolutePathT",
    bound=Union[HttpUrl, AbsoluteDirectory, AbsoluteFilePath, ZipPath],
)


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
            and (context := validation_context_var.get()).perform_io_checks
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
            and validation_context_var.get().perform_io_checks
            and not absolute.is_dir()
        ):
            raise ValueError(f"{absolute} does not point to an existing directory")

        return absolute


FileSource = Annotated[
    Union[HttpUrl, RelativeFilePath, FilePath],
    Field(union_mode="left_to_right"),
]
PermissiveFileSource = Union[FileSource, str, pydantic.HttpUrl]

V_suffix = TypeVar("V_suffix", bound=FileSource)
path_or_url_adapter: "TypeAdapter[Union[FilePath, DirectoryPath, HttpUrl]]" = (
    TypeAdapter(Union[FilePath, DirectoryPath, HttpUrl])
)


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
        src = value.absolute()
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
if TYPE_CHECKING:
    YamlValue = Union[YamlLeafValue, List["YamlValue"], Dict[YamlKey, "YamlValue"]]
else:
    # for pydantic validation we need to use `TypeAliasType`,
    # see https://docs.pydantic.dev/latest/concepts/types/#named-recursive-types
    # however this results in a partially unknown type with the current pyright 1.1.388
    YamlValue = _TypeAliasType(
        "YamlValue",
        Union[YamlLeafValue, List["YamlValue"], Dict[YamlKey, "YamlValue"]],
    )
BioimageioYamlContent = Dict[str, YamlValue]
BioimageioYamlSource = Union[PermissiveFileSource, BioimageioYamlContent]


def is_yaml_leaf_value(value: Any) -> TypeGuard[YamlLeafValue]:
    return isinstance(value, (bool, _date, _datetime, int, float, str, type(None)))


def is_yaml_list(value: Any) -> TypeGuard[List[YamlValue]]:
    return is_sequence(value) and all(is_yaml_value(item) for item in value)


def is_yaml_mapping(value: Any) -> TypeGuard[BioimageioYamlContent]:
    return is_mapping(value) and all(
        isinstance(key, str) and is_yaml_value(val) for key, val in value.items()
    )


def is_yaml_value(value: Any) -> TypeGuard[YamlValue]:
    return is_yaml_leaf_value(value) or is_yaml_list(value) or is_yaml_mapping(value)


@dataclass
class OpenedBioimageioYaml:
    content: BioimageioYamlContent
    original_root: Union[AbsoluteDirectory, RootHttpUrl, ZipFile]
    original_file_name: FileName


@dataclass
class LocalFile:
    path: FilePath
    original_root: Union[AbsoluteDirectory, RootHttpUrl, ZipFile]
    original_file_name: FileName


@dataclass
class FileInZip:
    path: ZipPath
    original_root: ZipFile
    original_file_name: FileName


class HashKwargs(TypedDict):
    sha256: NotRequired[Optional[Sha256]]


_file_source_adapter: TypeAdapter[Union[HttpUrl, RelativeFilePath, FilePath]] = (
    TypeAdapter(FileSource)
)


def interprete_file_source(file_source: PermissiveFileSource) -> FileSource:
    if isinstance(file_source, (HttpUrl, Path)):
        return file_source

    if isinstance(file_source, pydantic.AnyUrl):
        file_source = str(file_source)

    with validation_context_var.get().replace(perform_io_checks=False):
        strict = _file_source_adapter.validate_python(file_source)

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


class Progressbar(Protocol):
    count: int
    total: int

    def update(self, i: int): ...

    def reset(self): ...

    def close(self): ...


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
                folder = Path(mktemp())
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


def resolve(
    source: Union[PermissiveFileSource, FileDescr, ZipPath],
    /,
    progressbar: Union[Progressbar, bool, None] = None,
    **kwargs: Unpack[HashKwargs],
) -> Union[LocalFile, FileInZip]:
    """Resolve file `source` (download if needed)"""
    if isinstance(source, FileDescr):
        return source.download()
    elif isinstance(source, ZipPath):
        zip_root = source.root
        assert isinstance(zip_root, ZipFile)
        return FileInZip(
            source,
            zip_root,
            extract_file_name(source),
        )

    strict_source = interprete_file_source(source)
    if isinstance(strict_source, RelativeFilePath):
        strict_source = strict_source.absolute()
        if isinstance(strict_source, ZipPath):
            return FileInZip(
                strict_source, strict_source.root, extract_file_name(strict_source)
            )

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
            if progressbar is None:
                progressbar = False
        else:
            headers = {}
            if progressbar is None:
                progressbar = True

        if settings.user_agent is not None:
            headers["User-Agent"] = settings.user_agent

        downloader = pooch.HTTPDownloader(
            headers=headers,
            progressbar=progressbar,  # pyright: ignore[reportArgumentType]
        )
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

    return LocalFile(
        local_source,
        root,
        extract_file_name(strict_source),
    )


download = resolve


def resolve_and_extract(
    source: Union[PermissiveFileSource, FileDescr, ZipPath],
    /,
    progressbar: Union[Progressbar, bool, None] = None,
    **kwargs: Unpack[HashKwargs],
) -> LocalFile:
    """Resolve `source` within current ValidationContext,
    download if needed and
    extract file if within zip archive.

    note: If source points to a zip file it is not extracted
    """
    local = resolve(source, progressbar=progressbar)
    if isinstance(local, LocalFile):
        return local

    folder = extract(local.path)

    return LocalFile(
        folder / local.path.at,
        original_root=local.original_root,
        original_file_name=local.original_file_name,
    )


class LightHttpFileDescr(Node):
    """http source with sha256 value (minimal validation)"""

    source: pydantic.HttpUrl
    """file source"""

    sha256: Sha256
    """SHA256 checksum of the source file"""

    def download(self):
        return download(self.source, sha256=self.sha256)


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
    src: Union[pydantic.HttpUrl, HttpUrl, PurePath, RelativeFilePath, ZipPath],
) -> FileName:
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


@lru_cache
def get_sha256(path: Union[Path, ZipPath]) -> Sha256:
    """from https://stackoverflow.com/a/44873382"""
    desc = f"computing SHA256 of {path.name}"
    if isinstance(path, ZipPath):
        # no buffered reading available
        zf = path.root
        assert isinstance(zf, ZipFile)
        file_size = zf.NameToInfo[path.at].file_size
        pbar = tqdm(desc=desc, total=file_size)
        data = path.read_bytes()
        assert isinstance(data, bytes)
        h = hashlib.sha256(data)
    else:
        file_size = path.stat().st_size
        pbar = tqdm(desc=desc, total=file_size)
        h = hashlib.sha256()
        chunksize = 128 * 1024
        b = bytearray(chunksize)
        mv = memoryview(b)
        with open(path, "rb", buffering=0) as f:
            for n in iter(lambda: f.readinto(mv), 0):
                h.update(mv[:n])
                _ = pbar.update(n)

    sha = h.hexdigest()
    pbar.set_description(desc=desc + f" (result: {sha})")
    pbar.close()
    assert len(sha) == 64
    return Sha256(sha)
