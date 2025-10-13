import collections.abc
import io
import shutil
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
from zipfile import ZipFile

import httpx
import numpy
from loguru import logger
from numpy.typing import NDArray
from pydantic import BaseModel, FilePath, NewPath, RootModel
from ruyaml import YAML
from typing_extensions import Unpack

from ._settings import settings
from .io import (
    BIOIMAGEIO_YAML,
    BioimageioYamlContent,
    BioimageioYamlContentView,
    BytesReader,
    FileDescr,
    HashKwargs,
    LightHttpFileDescr,
    OpenedBioimageioYaml,
    RelativeFilePath,
    YamlValue,
    extract_file_name,
    find_bioimageio_yaml_file_name,
    get_reader,
    identify_bioimageio_yaml_file_name,
    interprete_file_source,
)
from .io_basics import AbsoluteDirectory, FileName, ZipPath
from .types import FileSource, PermissiveFileSource
from .url import HttpUrl, RootHttpUrl
from .utils import cache
from .validation_context import ValidationContext, get_validation_context

_yaml_load = YAML(typ="safe")

_yaml_dump = YAML()
_yaml_dump.version = (1, 2)  # pyright: ignore[reportAttributeAccessIssue]
_yaml_dump.default_flow_style = False
_yaml_dump.indent(mapping=2, sequence=4, offset=2)
_yaml_dump.width = 88  # pyright: ignore[reportAttributeAccessIssue]


def read_yaml(
    file: Union[FilePath, ZipPath, IO[str], IO[bytes], BytesReader, str],
) -> YamlValue:
    if isinstance(file, (ZipPath, Path)):
        data = file.read_text(encoding="utf-8")
    else:
        data = file

    content: YamlValue = _yaml_load.load(data)
    return content


def write_yaml(
    content: Union[YamlValue, BioimageioYamlContentView, BaseModel],
    /,
    file: Union[NewPath, FilePath, IO[str], IO[bytes], ZipPath],
):
    if isinstance(file, Path):
        cm = file.open("w", encoding="utf-8")
    else:
        cm = nullcontext(file)

    if isinstance(content, BaseModel):
        content = content.model_dump(mode="json")

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
                + f"to be strings (got '{key}' of type {type(key)})."
            )

    return cast(BioimageioYamlContent, content)


def _open_bioimageio_rdf_in_zip(
    path: ZipPath,
    *,
    original_root: Union[AbsoluteDirectory, RootHttpUrl, ZipFile],
    original_source_name: str,
) -> OpenedBioimageioYaml:
    with path.open("rb") as f:
        assert not isinstance(f, io.TextIOWrapper)
        unparsed_content = f.read().decode(encoding="utf-8")

    content = _sanitize_bioimageio_yaml(read_yaml(io.StringIO(unparsed_content)))

    return OpenedBioimageioYaml(
        content,
        original_root=original_root,
        original_file_name=extract_file_name(path),
        original_source_name=original_source_name,
        unparsed_content=unparsed_content,
    )


def _open_bioimageio_zip(
    source: ZipFile,
    *,
    original_source_name: str,
) -> OpenedBioimageioYaml:
    rdf_name = identify_bioimageio_yaml_file_name(
        [info.filename for info in source.filelist]
    )
    return _open_bioimageio_rdf_in_zip(
        ZipPath(source, rdf_name),
        original_root=source,
        original_source_name=original_source_name,
    )


def open_bioimageio_yaml(
    source: Union[PermissiveFileSource, ZipFile, ZipPath],
    /,
    **kwargs: Unpack[HashKwargs],
) -> OpenedBioimageioYaml:
    if isinstance(source, RelativeFilePath):
        source = source.absolute()

    if isinstance(source, ZipFile):
        return _open_bioimageio_zip(source, original_source_name=str(source))
    elif isinstance(source, ZipPath):
        return _open_bioimageio_rdf_in_zip(
            source, original_root=source.root, original_source_name=str(source)
        )

    try:
        if isinstance(source, (Path, str)) and (source_dir := Path(source)).is_dir():
            # open bioimageio yaml from a folder
            src = source_dir / find_bioimageio_yaml_file_name(source_dir)
        else:
            src = interprete_file_source(source)

        reader = get_reader(src, **kwargs)

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
                r = httpx.get(url, follow_redirects=True)
                _ = r.raise_for_status()
                unparsed_content = r.content.decode(encoding="utf-8")
                content = _sanitize_bioimageio_yaml(read_yaml(unparsed_content))
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
                    original_source_name=source,
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
        reader = entry.get_reader()
        with get_validation_context().replace(perform_io_checks=False):
            src = HttpUrl(entry.source)

    if reader.is_zipfile:
        return _open_bioimageio_zip(ZipFile(reader), original_source_name=str(src))

    unparsed_content = reader.read().decode(encoding="utf-8")
    content = _sanitize_bioimageio_yaml(read_yaml(unparsed_content))

    if isinstance(src, RelativeFilePath):
        src = src.absolute()

    if isinstance(src, ZipPath):
        root = src.root
    else:
        root = src.parent

    return OpenedBioimageioYaml(
        content,
        original_root=root,
        original_source_name=str(src),
        original_file_name=extract_file_name(src),
        unparsed_content=unparsed_content,
    )


_IdMap = RootModel[Dict[str, LightHttpFileDescr]]


def _get_id_map_impl(url: str) -> Dict[str, LightHttpFileDescr]:
    if not isinstance(url, str) or "/" not in url:
        logger.opt(depth=1).error("invalid id map url: {}", url)
    try:
        id_map_raw: Any = httpx.get(
            url, timeout=settings.http_timeout, follow_redirects=True
        ).json()
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
    content: Mapping[
        FileName,
        Union[
            str, FilePath, ZipPath, BioimageioYamlContentView, FileDescr, BytesReader
        ],
    ],
    zip: zipfile.ZipFile,
):
    """write strings as text, dictionaries as yaml and files to a ZipFile
    Args:
        content: dict mapping archive names to local file paths,
                 strings (for text files), or dict (for yaml files).
        zip: ZipFile
    """
    for arc_name, file in content.items():
        if isinstance(file, collections.abc.Mapping):
            buf = io.StringIO()
            write_yaml(file, buf)
            file = buf.getvalue()

        if isinstance(file, str):
            zip.writestr(arc_name, file.encode("utf-8"))
        else:
            if isinstance(file, BytesReader):
                reader = file
            else:
                reader = get_reader(file)

            if (
                isinstance(reader.original_root, ZipFile)
                and reader.original_root.filename == zip.filename
                and reader.original_file_name == arc_name
            ):
                logger.debug(
                    f"Not copying {reader.original_root}/{reader.original_file_name} to itself."
                )
                continue

            with zip.open(arc_name, "w") as dest:
                shutil.copyfileobj(reader, dest, 1024 * 8)


def write_zip(
    path: Union[FilePath, IO[bytes]],
    content: Mapping[
        FileName, Union[str, FilePath, ZipPath, BioimageioYamlContentView, BytesReader]
    ],
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
    reader = get_reader(source)
    if settings.allow_pickle:
        logger.warning("Loading numpy array with `allow_pickle=True`.")

    return numpy.load(reader, allow_pickle=settings.allow_pickle)


def save_array(path: Union[Path, ZipPath], array: NDArray[Any]) -> None:
    with path.open(mode="wb") as f:
        assert not isinstance(f, io.TextIOWrapper)
        return numpy.save(f, array, allow_pickle=False)
