import collections.abc
import io
import os
import platform
import shutil
import warnings
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile, mkdtemp
from typing import Any, Dict, Final, Literal, Mapping, Optional, Sequence, TextIO, TypedDict, Union, cast
from zipfile import ZIP_DEFLATED, ZipFile, is_zipfile

import pooch
from pydantic import AnyUrl, DirectoryPath, FilePath, HttpUrl, TypeAdapter
from ruamel.yaml import YAML
from typing_extensions import NotRequired, Unpack

from bioimageio.core.utils import get_parent_url
from bioimageio.spec import ResourceDescription
from bioimageio.spec import load_description as load_description
from bioimageio.spec._internal.base_nodes import ResourceDescriptionBase
from bioimageio.spec._internal.constants import DISCOVER
from bioimageio.spec._internal.types import (
    AbsoluteFilePath,
    FileName,
    FileSource,
    PermissiveFileSource,
    RdfContent,
    RelativeFilePath,
    Sha256,
    StrictFileSource,
    YamlValue,
)
from bioimageio.spec._internal.utils import extract_file_name
from bioimageio.spec._internal.validation_context import ValidationContext
from bioimageio.spec.description import InvalidDescription, dump_description
from bioimageio.spec.model.v0_4 import WeightsFormat
from bioimageio.spec.package import get_resource_package_content

if platform.machine() == "wasm32":
    import pyodide_http  # type: ignore

    pyodide_http.patch_all()


yaml = YAML(typ="safe")

RdfSource = Union[PermissiveFileSource, ResourceDescription, RdfContent]

LEGACY_RDF_NAMES: Final[Sequence[FileName]] = ("rdf.yaml",)


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
class _OpenedRdf:
    content: RdfContent
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


def _read_yaml(file: Union[FilePath, TextIO]) -> YamlValue:
    if isinstance(file, Path):
        cm = file.open("r", encoding="utf-8")
    else:
        cm = nullcontext(file)

    with cm as f:
        yaml.load(f)


def _write_yaml(content: YamlValue, /, file: Union[FilePath, TextIO]):
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


def _sanitize_bioimageio_yaml(content: YamlValue) -> RdfContent:
    if not isinstance(content, dict):
        raise ValueError(f"Expected bioimageio.yaml content to be a mapping (got {type(content)}).")

    for key in content:
        if not isinstance(key, str):
            raise ValueError(
                "Expected all keys (field names) in a bioimageio.yaml "
                f"need to be strings (got '{key}' of type {type(key)})."
            )

    return cast(RdfContent, content)


def read_description(
    rdf_source: FileSource,
    /,
    *,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
) -> Union[ResourceDescription, InvalidDescription]:
    rdf = _open_rdf(rdf_source)

    return load_description(
        rdf.content,
        context=ValidationContext(root=rdf.original_root, file_name=rdf.original_file_name),
        format_version=format_version,
    )


def write_description(rd: Union[ResourceDescription, RdfContent], /, file: Union[FilePath, TextIO]):
    if isinstance(rd, ResourceDescriptionBase):
        content = dump_description(rd)
    else:
        content = rd

    _write_yaml(cast(YamlValue, content), file)


def _prepare_resource_package(
    rdf_source: RdfSource,
    /,
    *,
    weights_priority_order: Optional[Sequence[WeightsFormat]] = None,
) -> Dict[FileName, Union[FilePath, RdfContent]]:
    """Prepare to package a resource description; downloads all required files.

    Args:
        rdf_source: A bioimage.io resource description (as file, raw YAML content or description class)
        context: validation context
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.
    """
    if isinstance(rdf_source, ResourceDescriptionBase):
        rd = rdf_source
        _ctxt = rd._internal_validation_context  # pyright: ignore[reportPrivateUsage]
        context = ValidationContext(root=_ctxt["root"], file_name=_ctxt["file_name"])
    elif isinstance(rdf_source, dict):
        context = ValidationContext()
        rd = load_description(
            rdf_source,
            context=context,
        )
    else:
        rdf = _open_rdf(rdf_source)
        context = ValidationContext(root=rdf.original_root, file_name=rdf.original_file_name)
        rd = load_description(
            rdf.content,
            context=context,
        )

    if isinstance(rd, InvalidDescription):
        raise ValueError(f"{rdf_source} is invalid: {rd.validation_summaries[0]}")

    package_content = get_resource_package_content(rd, weights_priority_order=weights_priority_order)

    local_package_content: Dict[FileName, Union[FilePath, RdfContent]] = {}
    for k, v in package_content.items():
        if not isinstance(v, collections.abc.Mapping):
            v = download(v, root=context.root).path

        local_package_content[k] = v

    return local_package_content


def _open_rdf(source: PermissiveFileSource, /, **kwargs: Unpack[HashKwargs]) -> _OpenedRdf:
    downloaded = download(source, **kwargs)
    local_source = downloaded.path
    root = downloaded.original_root

    if is_zipfile(local_source):
        local_source = _unzip(local_source)

    if local_source.is_dir():
        root = local_source
        local_source = local_source / _guess_description_file_name(local_source)

    content = _sanitize_bioimageio_yaml(_read_yaml(local_source))

    return _OpenedRdf(content, root, downloaded.original_file_name)


def _guess_description_file_name(path: Path) -> FileName:
    if path.is_file():
        if not is_zipfile(path):
            return path.name

        with ZipFile(path, "r") as f:
            candidates = [fname for fname in f.namelist() if fname.endswith(".bioimageio.yaml")]
            backup_candidates = [legacy for legacy in LEGACY_RDF_NAMES if legacy in f.namelist()]
    else:
        candidates = [p.name for p in path.glob("*.bioimageio.yaml")]
        backup_candidates = [legacy for legacy in LEGACY_RDF_NAMES if (path / legacy).exists()]

    if len(candidates) > 1:
        raise ValueError(f"Multiple RDFs in one package not yet supported (found {candidates}).")
    elif len(candidates) == 1:
        rdf_file_name = candidates[0]
    elif backup_candidates:
        rdf_file_name = backup_candidates[0]
    else:
        raise ValueError(f"No RDF found in {path}. (Looking for any '*.bioimageio.yaml' file or an 'rdf.yaml' file).")

    return rdf_file_name


def _unzip(file_path: FilePath, out_path: Optional[DirectoryPath] = None, overwrite: bool = True) -> DirectoryPath:
    if out_path is None:
        out_path = file_path.with_suffix(file_path.suffix + ".unzip")

    with ZipFile(file_path, "r") as f:
        if out_path.exists() and overwrite:
            if overwrite:
                warnings.warn(f"Overwriting existing unzipped archive at {out_path}")
            else:
                warnings.warn(f"Found already unzipped archive at {out_path}.")
                return out_path

        f.extractall(out_path)

    return out_path


def _write_zip(
    path: os.PathLike[str],
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
                _write_yaml(file, buf)
                file = buf.getvalue()

            if isinstance(file, str):
                myzip.writestr(arc_name, file.encode("utf-8"))
            else:
                myzip.write(file, arcname=arc_name)


def write_package(
    rdf_source: RdfSource,
    /,
    *,
    compression: int = ZIP_DEFLATED,
    compression_level: int = 1,
    output_path: Optional[os.PathLike[str]] = None,
    weights_priority_order: Optional[  # model only
        Sequence[
            Literal[
                "keras_hdf5",
                "onnx",
                "pytorch_state_dict",
                "tensorflow_js",
                "tensorflow_saved_model_bundle",
                "torchscript",
            ]
        ]
    ] = None,
) -> FilePath:
    """Package a bioimage.io resource as a zip file.

    Args:
        rd: bioimage.io resource description
        compression: The numeric constant of compression method.
        compression_level: Compression level to use when writing files to the archive.
                           See https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile
        output_path: file path to write package to
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.

    Returns:
        path to zipped bioimage.io package in BIOIMAGEIO_CACHE_PATH or 'output_path'
    """
    package_content = _prepare_resource_package(
        rdf_source,
        weights_priority_order=weights_priority_order,
    )
    if output_path is None:
        output_path = Path(NamedTemporaryFile(suffix=".bioimageio.zip", delete=False).name)
    else:
        output_path = Path(output_path)

    _write_zip(output_path, package_content, compression=compression, compression_level=compression_level)
    return output_path


def write_package_as_folder(
    rdf_source: RdfSource,
    /,
    *,
    output_path: Optional[DirectoryPath] = None,
    weights_priority_order: Optional[  # model only
        Sequence[
            Literal[
                "keras_hdf5",
                "onnx",
                "pytorch_state_dict",
                "tensorflow_js",
                "tensorflow_saved_model_bundle",
                "torchscript",
            ]
        ]
    ] = None,
) -> DirectoryPath:
    """Write the content of a bioimage.io resource package to a folder.

    Args:
        rd: bioimage.io resource description
        output_path: file path to write package to
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.

    Returns:
        path to zipped bioimage.io package in BIOIMAGEIO_CACHE_PATH or 'output_path'
    """
    package_content = _prepare_resource_package(
        rdf_source,
        weights_priority_order=weights_priority_order,
    )
    if output_path is None:
        output_path = Path(mkdtemp())
    else:
        output_path = Path(output_path)

    for name, source in package_content.items():
        if isinstance(source, collections.abc.Mapping):
            _write_yaml(cast(YamlValue, source), output_path / name)
        else:
            shutil.copy(source, output_path / name)

    return output_path
