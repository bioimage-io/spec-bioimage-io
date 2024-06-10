import io
import warnings
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import (
    IO,
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    TextIO,
    Union,
    cast,
)
from zipfile import ZipFile, is_zipfile

import numpy
import requests
from loguru import logger
from numpy.typing import NDArray
from pydantic import DirectoryPath, FilePath, NewPath
from ruyaml import YAML
from typing_extensions import Unpack

from ._settings import settings
from .io import (
    BIOIMAGEIO_YAML,
    SLOTS,
    BioimageioYamlContent,
    FileDescr,
    HashKwargs,
    OpenedBioimageioYaml,
    YamlValue,
    download,
    find_bioimageio_yaml_file_name,
)
from .io_basics import FileName, Sha256
from .types import FileSource, PermissiveFileSource
from .utils import cache

yaml = YAML(typ="safe")


def read_yaml(file: Union[FilePath, TextIO]) -> YamlValue:
    if isinstance(file, Path):
        cm = file.open("r", encoding="utf-8")
    else:
        cm = nullcontext(file)

    with cm as f:
        content: YamlValue = yaml.load(f)

    return content


def write_yaml(
    content: Union[YamlValue, Dict[str, YamlValue]],
    /,
    file: Union[NewPath, FilePath, TextIO],
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


def open_bioimageio_yaml(
    source: PermissiveFileSource, /, **kwargs: Unpack[HashKwargs]
) -> OpenedBioimageioYaml:
    try:
        downloaded = download(source, **kwargs)
    except Exception:
        # check if `source` is a collection id
        if (
            not isinstance(source, str)
            or not isinstance(settings.collection, str)
            or "/" not in settings.collection
        ):
            raise

        collection = get_collection()
        if source not in collection:
            if isinstance(source, str) and source.endswith("/draft"):
                if settings.resolve_draft:
                    collection_url = settings.collection_draft
                else:
                    collection_url = ""
                    logger.error(
                        "Did not try to resolve '{}' as BIOIMAGEIO_RESOLVE_DRAFT is set to False",
                        source,
                    )
            else:
                collection_url = settings.collection

            logger.error("'{}' not found in collection {}", source, collection_url)
            raise

        entry = collection[source]
        logger.info(
            "{} loading {}/{} from {}",
            entry.emoji,
            entry.id,
            entry.version,
            entry.url,
        )
        downloaded = download(entry.url, sha256=entry.sha256)

    local_source = downloaded.path
    root = downloaded.original_root

    if is_zipfile(local_source):
        local_source = unzip(local_source)

    if local_source.is_dir():
        root = local_source
        local_source = local_source / find_bioimageio_yaml_file_name(local_source)

    content = _sanitize_bioimageio_yaml(read_yaml(local_source))

    return OpenedBioimageioYaml(content, root, downloaded.original_file_name)


@dataclass(frozen=True, **SLOTS)
class CollectionEntry:
    """collection entry

    note: The BioImage.IO collection is still under development;
          this collection entry might change in the future!
    """

    id: str
    """concept id of the resource; to identify a resource version use <id>/<version>.
    See `version` below."""
    version: str
    """version. To identify a resource version use <id>/<version> for reference"""
    emoji: str
    """a Unicode emoji string symbolizing this resource"""
    url: str
    """Resource Description File (RDF) URL"""
    sha256: Optional[Sha256]
    """SHA256 hash value of RDF"""
    doi: Optional[str]
    """DOI (regsitered through zenodo.org)
    as alternative reference of this bioimage.io upload."""


def _get_one_collection(url: str):
    ret: Dict[str, CollectionEntry] = {}
    if not isinstance(url, str) or "/" not in url:
        logger.error("invalid collection url: {}", url)
    try:
        collection: List[Dict[Any, Any]] = (
            requests.get(url, timeout=5).json().get("collection")
        )
    except Exception as e:
        logger.error("failed to get {}: {}", url, e)
        return ret

    if not isinstance(collection, list):
        logger.error("`collection` field of {} has type {}", url, type(collection))
        return ret

    for raw_entry in collection:
        assert isinstance(raw_entry, dict), type(raw_entry)
        v: Any
        d: Any
        try:
            for i, (v, d) in enumerate(zip(raw_entry["versions"], raw_entry["dois"])):
                entry = CollectionEntry(
                    id=raw_entry["id"],
                    emoji=raw_entry.get("id_emoji", raw_entry.get("nickname_icon", "")),
                    url=raw_entry["rdf_source"],
                    sha256=raw_entry["rdf_sha256"],
                    version=v,
                    doi=d,
                )
                ret[f"{raw_entry['id']}/{v}"] = entry
                if i == 0:
                    # latest version
                    ret[raw_entry["id"]] = entry
                    if (concept_doi := raw_entry.get("concept_doi")) is not None:
                        ret[concept_doi] = entry

                    if (nickname := raw_entry.get("nickname")) is not None:
                        ret[nickname] = entry

                if d is not None:
                    ret[d] = entry

        except Exception as e:
            entry_id = (
                raw_entry.get("id", "unknown")
                if isinstance(raw_entry, dict)
                else "unknown"
            )
            logger.error(
                "failed to parse collection entry with `id={}`: {}", entry_id, e
            )
            continue

    return ret


@cache
def get_collection() -> Mapping[str, CollectionEntry]:
    try:
        if settings.resolve_draft:
            ret = _get_one_collection(settings.collection_draft)
        else:
            ret = {}

        ret.update(_get_one_collection(settings.collection))

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
            raise ValueError("Missing argument: out_path")
    else:
        zip_context = ZipFile(zip_file, "r")
        if out_path is None:
            out_path = zip_file.with_suffix(zip_file.suffix + ".unzip")

    with zip_context as f:
        if out_path.exists() and overwrite:
            if overwrite:
                warnings.warn(f"Overwriting existing unzipped archive at {out_path}")
            else:
                found_content = {
                    p.relative_to(out_path).as_posix() for p in out_path.glob("*")
                }
                expected_content = {info.filename for info in f.filelist}
                if expected_content - found_content:
                    warnings.warn(
                        f"Unzipped archive at {out_path} is missing expected files."
                    )
                    parts = out_path.name.split("_")
                    nr, *suffixes = parts[-1].split(".")
                    if nr.isdecimal():
                        nr = str(int(nr) + 1)
                    else:
                        nr = f"1.{nr}"

                    parts[-1] = ".".join([nr, *suffixes])
                    return unzip(
                        f, out_path.with_name("_".join(parts)), overwrite=overwrite
                    )
                else:
                    warnings.warn(
                        "Using already unzipped archive with all expected files at"
                        + f" {out_path}."
                    )
                    return out_path

        f.extractall(out_path)

    return out_path


def write_zip(
    path: Union[FilePath, IO[bytes]],
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
    with ZipFile(
        path, "w", compression=compression, compresslevel=compression_level
    ) as myzip:
        for arc_name, file in content.items():
            if isinstance(file, dict):
                buf = io.StringIO()
                write_yaml(file, buf)
                file = buf.getvalue()

            if isinstance(file, str):
                myzip.writestr(arc_name, file.encode("utf-8"))
            else:
                myzip.write(file, arcname=arc_name)


def load_array(source: Union[FileSource, FileDescr]) -> NDArray[Any]:
    path = download(source).path

    return numpy.load(path, allow_pickle=False)


def save_array(path: Path, array: NDArray[Any]) -> None:
    return numpy.save(path, array, allow_pickle=False)
