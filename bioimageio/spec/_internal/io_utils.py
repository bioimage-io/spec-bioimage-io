import io
import zipfile
from contextlib import nullcontext
from difflib import get_close_matches
from pathlib import Path
from types import MappingProxyType
from typing import (
    IO,
    Any,
    Dict,
    Mapping,
    Union,
    cast,
)
from zipfile import ZipFile, is_zipfile

import numpy
import requests
from loguru import logger
from numpy.typing import NDArray
from pydantic import FilePath, NewPath, RootModel
from ruyaml import YAML
from typing_extensions import Unpack

from ._settings import settings
from .io import (
    BIOIMAGEIO_YAML,
    BioimageioYamlContent,
    FileDescr,
    FileInZip,
    HashKwargs,
    LightHttpFileDescr,
    OpenedBioimageioYaml,
    YamlValue,
    find_bioimageio_yaml_file_name,
    identify_bioimageio_yaml_file_name,
    resolve,
)
from .io_basics import FileName, ZipPath
from .types import FileSource, PermissiveFileSource
from .url import HttpUrl
from .utils import cache
from .validation_context import ValidationContext

_yaml_load = YAML(typ="safe")

_yaml_dump = YAML()
_yaml_dump.version = (1, 2)  # pyright: ignore[reportAttributeAccessIssue]
_yaml_dump.default_flow_style = False
_yaml_dump.indent(mapping=2, sequence=4, offset=2)
_yaml_dump.width = 88  # pyright: ignore[reportAttributeAccessIssue]


def read_yaml(file: Union[FilePath, ZipPath, IO[str], IO[bytes]]) -> YamlValue:
    if isinstance(file, (ZipPath, Path)):
        data = file.read_text(encoding="utf-8")
    else:
        data = file

    content: YamlValue = _yaml_load.load(data)
    return content


def write_yaml(
    content: Union[YamlValue, BioimageioYamlContent],
    /,
    file: Union[NewPath, FilePath, IO[str], IO[bytes], ZipPath],
):
    if isinstance(file, Path):
        cm = file.open("w", encoding="utf-8")
    else:
        cm = nullcontext(file)

    with cm as f:
        _yaml_dump.dump(content, f)


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
        unparsed_content = f.read().decode(encoding="utf-8")

    content = _sanitize_bioimageio_yaml(read_yaml(io.StringIO(unparsed_content)))

    return OpenedBioimageioYaml(
        content,
        source,
        source.filename or "bioimageio.zip",
        unparsed_content=unparsed_content,
    )


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
        if isinstance(source, (Path, str)) and (source_dir := Path(source)).is_dir():
            # open bioimageio yaml from a folder
            src = source_dir / find_bioimageio_yaml_file_name(source_dir)
        else:
            src = source

        downloaded = resolve(src, **kwargs)

    except Exception:
        # check if `source` is a collection id
        if (
            not isinstance(source, str)
            or not isinstance(settings.id_map, str)
            or "/" not in settings.id_map
        ):
            raise

        if settings.collection_http_pattern:
            with ValidationContext(perform_io_checks=False):
                url = HttpUrl(
                    settings.collection_http_pattern.format(bioimageio_id=source)
                )

            try:
                r = requests.get(url)
                r.raise_for_status()
                unparsed_content = r.content.decode(encoding="utf-8")
                content = _sanitize_bioimageio_yaml(
                    read_yaml(io.StringIO(unparsed_content))
                )
            except Exception as e:
                logger.warning("Failed to get bioimageio.yaml from {}: {}", url, e)
            else:
                original_file_name = (
                    "rdf.yaml" if url.path is None else url.path.split("/")[-1]
                )
                return OpenedBioimageioYaml(
                    content=content,
                    original_root=url.parent,
                    original_file_name=original_file_name,
                    unparsed_content=unparsed_content,
                )

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
    if isinstance(local_source, ZipPath):
        return _open_bioimageio_rdf_in_zip(local_source.root, local_source.name)
    elif is_zipfile(local_source):
        return _open_bioimageio_zip(ZipFile(local_source))

    if local_source.is_dir():
        root = local_source
        local_source = local_source / find_bioimageio_yaml_file_name(local_source)
    else:
        root = downloaded.original_root

    content = _sanitize_bioimageio_yaml(read_yaml(local_source))
    return OpenedBioimageioYaml(
        content,
        root.original_root if isinstance(root, FileInZip) else root,
        downloaded.original_file_name,
        unparsed_content=local_source.read_text(encoding="utf-8"),
    )


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


def write_content_to_zip(
    content: Mapping[FileName, Union[str, FilePath, ZipPath, Dict[Any, Any]]],
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
        elif isinstance(file, ZipPath):
            zip.writestr(arc_name, file.read_bytes())
        else:
            zip.write(file, arcname=arc_name)


def write_zip(
    path: Union[FilePath, IO[bytes]],
    content: Mapping[FileName, Union[str, FilePath, ZipPath, Dict[Any, Any]]],
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


def load_array(source: Union[FileSource, FileDescr, ZipPath]) -> NDArray[Any]:
    path = resolve(source).path
    with path.open(mode="rb") as f:
        assert not isinstance(f, io.TextIOWrapper)
        return numpy.load(f, allow_pickle=False)


def save_array(path: Union[Path, ZipPath], array: NDArray[Any]) -> None:
    with path.open(mode="wb") as f:
        assert not isinstance(f, io.TextIOWrapper)
        return numpy.save(f, array, allow_pickle=False)
