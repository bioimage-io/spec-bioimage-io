import io
import os
import platform
import warnings
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Final, Literal, Mapping, Optional, Sequence, TextIO, TypedDict, Union, cast
from zipfile import ZipFile, is_zipfile

import pooch
from pydantic import AnyUrl, DirectoryPath, FilePath, HttpUrl, TypeAdapter
from ruamel.yaml import YAML
from typing_extensions import NotRequired, Unpack

from bioimageio.spec import ResourceDescription
from bioimageio.spec._description import InvalidDescription, build_description, dump_description
from bioimageio.spec._internal.base_nodes import ResourceDescriptionBase
from bioimageio.spec._internal.constants import DISCOVER
from bioimageio.spec._internal.types import (
    AbsoluteFilePath,
    BioimageioYamlContent,
    FileName,
    FileSource,
    PermissiveFileSource,
    RelativeFilePath,
    Sha256,
    StrictFileSource,
    YamlValue,
)
from bioimageio.spec._internal.types._file_source import extract_file_name
from bioimageio.spec._internal.utils import get_parent_url
from bioimageio.spec._internal.validation_context import ValidationContext

if platform.machine() == "wasm32":
    import pyodide_http  # type: ignore

    pyodide_http.patch_all()


yaml = YAML(typ="safe")

BioimageioYamlSource = Union[PermissiveFileSource, ResourceDescription, BioimageioYamlContent]

BIOIMAGEIO_YAML = "bioimageio.yaml"
LEGACY_BIOIMAGEIO_YAML_NAMES: Final[Sequence[FileName]] = ("rdf.yaml", "model.yaml")


class HashKwargs(TypedDict):
    sha256: NotRequired[Optional[Sha256]]


def _get_known_hash(hash_kwargs: HashKwargs):
    if "sha256" in hash_kwargs:
        return f"sha256:{hash_kwargs['sha256']}"
    else:
        return None


@dataclass
class DownloadedFile:
    path: AbsoluteFilePath
    original_root: Union[AnyUrl, DirectoryPath]
    original_file_name: str


@dataclass
class OpenedBioimageioYaml:
    content: BioimageioYamlContent
    original_root: Union[AnyUrl, DirectoryPath]
    original_file_name: str


def _interprete_file_source(file_source: PermissiveFileSource, root: Union[HttpUrl, DirectoryPath]) -> StrictFileSource:
    source = TypeAdapter(FileSource).validate_python(file_source)
    if isinstance(source, RelativeFilePath):
        source = source.get_absolute(root)

    return source

    # todo: prettier file source validation error
    # try:
    # except ValidationError as e:


def read_yaml(file: Union[FilePath, TextIO]) -> YamlValue:
    if isinstance(file, Path):
        cm = file.open("r", encoding="utf-8")
    else:
        cm = nullcontext(file)

    with cm as f:
        yaml.load(f)


def write_yaml(content: YamlValue, /, file: Union[FilePath, TextIO]):
    if isinstance(file, Path):
        cm = file.open("w", encoding="utf-8")
    else:
        cm = nullcontext(file)

    with cm as f:
        yaml.dump(content, f)


def download(
    source: PermissiveFileSource,
    /,
    root: Union[DirectoryPath, HttpUrl] = Path(),  # root to resolve relative file paths
    **kwargs: Unpack[HashKwargs],
) -> DownloadedFile:
    strict_source = _interprete_file_source(source, root)
    if isinstance(strict_source, AnyUrl):
        if strict_source.scheme not in ("http", "https"):
            raise NotImplementedError(strict_source.scheme)

        if os.environ.get("CI", "false").lower() in ("1", "t", "true", "yes", "y"):
            headers = {"User-Agent": "ci"}
            progressbar = False
        else:
            headers = {}
            progressbar = True

        if (user_agent := os.environ.get("BIOIMAGEIO_USER_AGENT")) is not None:
            headers["User-Agent"] = user_agent

        downloader = pooch.HTTPDownloader(headers=headers, progressbar=progressbar)
        _ls: Any = pooch.retrieve(url=str(strict_source), known_hash=_get_known_hash(kwargs), downloader=downloader)
        local_source = Path(_ls).absolute()
        root = get_parent_url(strict_source)
    else:
        local_source = strict_source
        root = strict_source.parent

    return DownloadedFile(
        local_source,
        root,
        extract_file_name(strict_source),
    )


def _sanitize_bioimageio_yaml(content: YamlValue) -> BioimageioYamlContent:
    if not isinstance(content, dict):
        raise ValueError(f"Expected bioimageio.yaml content to be a mapping (got {type(content)}).")

    for key in content:
        if not isinstance(key, str):
            raise ValueError(
                "Expected all keys (field names) in a bioimageio.yaml "
                f"need to be strings (got '{key}' of type {type(key)})."
            )

    return cast(BioimageioYamlContent, content)


def load_description(
    source: FileSource,
    /,
    *,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
) -> Union[ResourceDescription, InvalidDescription]:
    opened = open_bioimageio_yaml(source)

    return build_description(
        opened.content,
        context=ValidationContext(root=opened.original_root, file_name=opened.original_file_name),
        format_version=format_version,
    )


def save_description(rd: Union[ResourceDescription, BioimageioYamlContent], /, file: Union[FilePath, TextIO]):
    if isinstance(rd, ResourceDescriptionBase):
        content = dump_description(rd)
    else:
        content = rd

    write_yaml(cast(YamlValue, content), file)


def open_bioimageio_yaml(source: PermissiveFileSource, /, **kwargs: Unpack[HashKwargs]) -> OpenedBioimageioYaml:
    downloaded = download(source, **kwargs)
    local_source = downloaded.path
    root = downloaded.original_root

    if is_zipfile(local_source):
        local_source = unzip(local_source)

    if local_source.is_dir():
        root = local_source
        local_source = local_source / find_description_file_name(local_source)

    content = _sanitize_bioimageio_yaml(read_yaml(local_source))

    return OpenedBioimageioYaml(content, root, downloaded.original_file_name)


def find_description_file_name(path: Path) -> FileName:
    if path.is_file():
        if not is_zipfile(path):
            return path.name

        with ZipFile(path, "r") as f:
            if BIOIMAGEIO_YAML in f.namelist():
                return BIOIMAGEIO_YAML

            candidates = [fname for fname in f.namelist() if fname.endswith(".{BIOIMAGEIO_YAML}")] + [
                legacy for legacy in LEGACY_BIOIMAGEIO_YAML_NAMES if legacy in f.namelist()
            ]
    else:
        if (path / BIOIMAGEIO_YAML).exists():
            return BIOIMAGEIO_YAML

        candidates = [p.name for p in path.glob(f"*.{BIOIMAGEIO_YAML}")] + [
            legacy for legacy in LEGACY_BIOIMAGEIO_YAML_NAMES if (path / legacy).exists()
        ]

    if len(candidates) == 0:
        raise ValueError(
            f"No bioimageio.yaml found in {path}. (Looking for '{BIOIMAGEIO_YAML}', "
            f"any file with the '.{BIOIMAGEIO_YAML}' extension, or any legacy file: {LEGACY_BIOIMAGEIO_YAML_NAMES})."
        )

    candidates.sort()
    return candidates[0]


def unzip(zip_file: FilePath, out_path: Optional[DirectoryPath] = None, overwrite: bool = True) -> DirectoryPath:
    if out_path is None:
        out_path = zip_file.with_suffix(zip_file.suffix + ".unzip")

    with ZipFile(zip_file, "r") as f:
        if out_path.exists() and overwrite:
            if overwrite:
                warnings.warn(f"Overwriting existing unzipped archive at {out_path}")
            else:
                warnings.warn(f"Found already unzipped archive at {out_path}.")
                return out_path

        f.extractall(out_path)

    return out_path


def write_zip(
    path: FilePath,
    content: Mapping[FileName, Union[str, FilePath, Dict[Any, Any]]],
    *,
    compression: int,
    compression_level: int,
) -> None:
    """Write a zip archive.

    Args:
        path: output path to write to.
        content: dict mapping archive names to local file paths, strings (for text files), or dict (for yaml files).
        compression: The numeric constant of compression method.
        compression_level: Compression level to use when writing files to the archive.
                           See https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile

    """
    with ZipFile(path, "w", compression=compression, compresslevel=compression_level) as myzip:
        for arc_name, file in content.items():
            if isinstance(file, dict):
                buf = io.StringIO()
                write_yaml(file, buf)
                file = buf.getvalue()

            if isinstance(file, str):
                myzip.writestr(arc_name, file.encode("utf-8"))
            else:
                myzip.write(file, arcname=arc_name)
