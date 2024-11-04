import io
import warnings
import zipfile
from contextlib import nullcontext
from difflib import get_close_matches
from pathlib import Path
from tempfile import mktemp
from types import MappingProxyType
from typing import (
    IO,
    Any,
    Dict,
    Mapping,
    Optional,
    Union,
    cast,
)
from zipfile import ZipFile, is_zipfile

import numpy
import requests
from loguru import logger
from numpy.typing import NDArray
from pydantic import DirectoryPath, FilePath, NewPath, RootModel
from ruyaml import YAML
from typing_extensions import Unpack

from ._settings import settings
from .io import (
    BIOIMAGEIO_YAML,
    BioimageioYamlContent,
    FileDescr,
    HashKwargs,
    LightHttpFileDescr,
    OpenedBioimageioYaml,
    YamlValue,
    download,
    find_bioimageio_yaml_file_name,
    identify_bioimageio_yaml_file_name,
)
from .io_basics import FileName
from .types import FileSource, PermissiveFileSource
from .utils import cache

yaml = YAML(typ="safe")


def read_yaml(file: Union[FilePath, IO[str], IO[bytes]]) -> YamlValue:
    if isinstance(file, Path):
        cm = file.open("r", encoding="utf-8")
    else:
        cm = nullcontext(file)

    with cm as f:
        content: YamlValue = yaml.load(f)

    return content


def write_yaml(
    content: YamlValue, /, file: Union[NewPath, FilePath, IO[str], IO[bytes]]
):
    if isinstance(file, Path):
        cm = file.open("w", encoding="utf-8")
    else:
        cm = nullcontext(file)

    with cm as f:
        yaml.dump(content, f)


def _sanitize_bioimageio_yaml(content: YamlValue) -> BioimageioYamlContent:
    if not isinstance(content, dict):
        raise ValueError(
            f"Expected {BIOIMAGEIO_YAML} content to be a mapping (got {type(content)})."
        )

    for key in content:
        if not isinstance(key, str):
            raise ValueError(
                f"Expected all keys (field names) in a {BIOIMAGEIO_YAML} "
                + f"need to be strings (got '{key}' of type {type(key)})."
            )

    return cast(BioimageioYamlContent, content)


def _open_bioimageio_rdf_in_zip(source: ZipFile, rdf_name: str) -> OpenedBioimageioYaml:
    with source.open(rdf_name) as f:
        content = _sanitize_bioimageio_yaml(read_yaml(f))

    return OpenedBioimageioYaml(content, source, source.filename or "bioimageio.zip")


def _open_bioimageio_zip(source: ZipFile) -> OpenedBioimageioYaml:
    rdf_name = identify_bioimageio_yaml_file_name(
        [info.filename for info in source.filelist]
    )
    return _open_bioimageio_rdf_in_zip(source, rdf_name)


def open_bioimageio_yaml(
    source: Union[PermissiveFileSource, ZipFile], /, **kwargs: Unpack[HashKwargs]
) -> OpenedBioimageioYaml:
    if isinstance(source, ZipFile):
        return _open_bioimageio_zip(source)

    try:
        downloaded = download(source, **kwargs)
    except Exception:
        # check if `source` is a collection id
        if (
            not isinstance(source, str)
            or not isinstance(settings.id_map, str)
            or "/" not in settings.id_map
        ):
            raise

        id_map = get_id_map()
        if id_map and source not in id_map:
            close_matches = get_close_matches(source, id_map)
            if len(close_matches) == 0:
                raise

            if len(close_matches) == 1:
                did_you_mean = f" Did you mean '{close_matches[0]}'?"
            else:
                did_you_mean = f" Did you mean any of {close_matches}?"

            raise FileNotFoundError(f"'{source}' not found.{did_you_mean}")

        entry = id_map[source]
        logger.info("loading {} from {}", source, entry.source)
        downloaded = entry.download()

    local_source = downloaded.path
    if isinstance(local_source, zipfile.Path):
        return _open_bioimageio_rdf_in_zip(local_source.root, local_source.name)
    elif is_zipfile(local_source):
        return _open_bioimageio_zip(ZipFile(local_source))

    if local_source.is_dir():
        root = local_source
        local_source = local_source / find_bioimageio_yaml_file_name(local_source)
    else:
        root = downloaded.original_root

    content = _sanitize_bioimageio_yaml(read_yaml(local_source))
    return OpenedBioimageioYaml(content, root, downloaded.original_file_name)


_IdMap = RootModel[Dict[str, LightHttpFileDescr]]


def _get_id_map_impl(url: str) -> Dict[str, LightHttpFileDescr]:
    if not isinstance(url, str) or "/" not in url:
        logger.opt(depth=1).error("invalid id map url: {}", url)
    try:
        id_map_raw: Any = requests.get(url, timeout=10).json()
    except Exception as e:
        logger.opt(depth=1).error("failed to get {}: {}", url, e)
        return {}

    id_map = _IdMap.model_validate(id_map_raw)
    return id_map.root


@cache
def get_id_map() -> Mapping[str, LightHttpFileDescr]:
    try:
        if settings.resolve_draft:
            ret = _get_id_map_impl(settings.id_map_draft)
        else:
            ret = {}

        ret.update(_get_id_map_impl(settings.id_map))

    except Exception as e:
        logger.error("failed to get resource id mapping: {}", e)
        ret = {}

    return MappingProxyType(ret)


def unzip(
    zip_file: Union[FilePath, ZipFile],
    out_path: Optional[DirectoryPath] = None,
    overwrite: bool = False,
) -> DirectoryPath:
    if isinstance(zip_file, ZipFile):
        zip_context = nullcontext(zip_file)
        if out_path is None:
            if zip_file.filename is None:
                out_path = Path(mktemp())
            else:
                zip_path = Path(zip_file.filename)
                out_path = zip_path.with_suffix(zip_path.suffix + ".unzip")
    else:
        zip_context = ZipFile(zip_file, "r")
        if out_path is None:
            out_path = zip_file.with_suffix(zip_file.suffix + ".unzip")

    if overwrite and out_path.exists():
        warnings.warn(f"Overwriting existing unzipped archive at {out_path}")

    with zip_context as f:
        if overwrite or not out_path.exists():
            f.extractall(out_path)
            return out_path

        found_content = {p.relative_to(out_path).as_posix() for p in out_path.glob("*")}
        expected_content = {info.filename for info in f.filelist}
        if expected_missing := expected_content - found_content:
            parts = out_path.name.split("_")
            nr, *suffixes = parts[-1].split(".")
            if nr.isdecimal():
                nr = str(int(nr) + 1)
            else:
                nr = f"1.{nr}"

            parts[-1] = ".".join([nr, *suffixes])
            out_path_new = out_path.with_name("_".join(parts))
            warnings.warn(
                f"Unzipped archive at {out_path} is missing expected files"
                + f" {expected_missing}."
                + f" Unzipping to {out_path_new} instead to avoid overwriting."
            )
            return unzip(f, out_path_new, overwrite=overwrite)
        else:
            warnings.warn(
                f"Found unzipped archive with all expected files at {out_path}."
            )
            return out_path


def write_content_to_zip(
    content: Mapping[FileName, Union[str, FilePath, zipfile.Path, Dict[Any, Any]]],
    zip: zipfile.ZipFile,
):
    """write strings as text, dictionaries as yaml and files to a ZipFile
    Args:
        content: dict mapping archive names to local file paths,
                 strings (for text files), or dict (for yaml files).
        zip: ZipFile
    """
    for arc_name, file in content.items():
        if isinstance(file, dict):
            buf = io.StringIO()
            write_yaml(file, buf)
            file = buf.getvalue()

        if isinstance(file, str):
            zip.writestr(arc_name, file.encode("utf-8"))
        elif isinstance(file, zipfile.Path):
            zip.writestr(arc_name, file.open("rb").read())
        else:
            zip.write(file, arcname=arc_name)


def write_zip(
    path: Union[FilePath, IO[bytes]],
    content: Mapping[FileName, Union[str, FilePath, zipfile.Path, Dict[Any, Any]]],
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
    with ZipFile(
        path, "w", compression=compression, compresslevel=compression_level
    ) as zip:
        write_content_to_zip(content, zip)


def load_array(source: Union[FileSource, FileDescr]) -> NDArray[Any]:
    path = download(source).path
    with path.open(mode="rb") as f:
        return numpy.load(f, allow_pickle=False)


def save_array(path: Union[Path, zipfile.Path], array: NDArray[Any]) -> None:
    with path.open(mode="wb") as f:
        return numpy.save(f, array, allow_pickle=False)
