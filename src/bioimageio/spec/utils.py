"""Utility functions for bioimage.io specifications (mostly IO)."""

import json
from pathlib import Path, PurePosixPath
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)

from imageio.v3 import imread
from loguru import logger
from numpy.typing import NDArray
from typing_extensions import assert_never

from ._description import ensure_description_is_dataset, ensure_description_is_model
from ._internal.io import (
    download,
    extract_file_name,
    get_reader,
    get_sha256,
    identify_bioimageio_yaml_file_name,
    interprete_file_source,
    is_valid_bioimageio_yaml_name,
)
from ._internal.io_basics import Suffix, ZipPath
from ._internal.io_utils import (
    load_array,
    open_bioimageio_yaml,
    read_yaml,
    save_array,
    write_yaml,
)
from ._internal.type_guards import is_ndarray
from ._internal.types import FileSource, PermissiveFileSource, RelativeFilePath
from ._internal.url import HttpUrl
from ._internal.utils import files

DEFAULT_H5_DATASET_PATH = "data"


SUFFIXES_WITH_DATAPATH = (".h5", ".hdf", ".hdf5")

_SourceT = TypeVar("_SourceT", Path, HttpUrl, ZipPath)

__all__ = [
    "download",
    "ensure_description_is_dataset",
    "ensure_description_is_model",
    "extract_file_name",
    "get_file_name",
    "get_reader",
    "get_sha256",
    "get_spdx_licenses",
    "identify_bioimageio_yaml_file_name",
    "is_valid_bioimageio_yaml_name",
    "load_array",
    "load_image",
    "open_bioimageio_yaml",
    "read_yaml",
    "save_array",
    "SpdxLicenseEntry",
    "SpdxLicenses",
    "write_yaml",
]

get_file_name = extract_file_name


class SpdxLicenseEntry(TypedDict):
    isDeprecatedLicenseId: bool
    isKnownByZenodo: bool
    isOsiApproved: bool
    licenseId: str
    name: str
    reference: str


class SpdxLicenses(TypedDict):
    licenseListVersion: str
    licenses: List[SpdxLicenseEntry]
    releaseDate: str


def get_spdx_licenses() -> SpdxLicenses:
    """get details of the SPDX licenses known to bioimageio.spec"""
    with (
        files("bioimageio.spec")
        .joinpath("static/spdx_licenses.json")
        .open("r", encoding="utf-8")
    ) as f:
        return json.load(f)


def get_bioimageio_json_schema() -> Dict[str, Any]:
    """get the bioimageio specification as a JSON schema"""
    with (
        files("bioimageio.spec")
        .joinpath("static/bioimageio_schema.json")
        .open("r", encoding="utf-8")
    ) as f:
        return json.load(f)


def load_image(source: Union[ZipPath, PermissiveFileSource]) -> NDArray[Any]:
    """load a single image as numpy array

    Args:
        source: image source
    """

    if isinstance(source, ZipPath):
        parsed_source = source
    else:
        parsed_source = interprete_file_source(source)

    if isinstance(parsed_source, RelativeFilePath):
        src = parsed_source.absolute()
    else:
        src = parsed_source

    if isinstance(src, Path):
        file_source, suffix, subpath = split_dataset_path(src)
    elif isinstance(src, HttpUrl):
        file_source, suffix, subpath = split_dataset_path(src)
    elif isinstance(src, ZipPath):
        file_source, suffix, subpath = split_dataset_path(src)
    else:
        assert_never(src)

    if suffix == ".npy":
        if subpath is not None:
            logger.warning(
                "Unexpected subpath {} for .npy source {}", subpath, file_source
            )

        image = load_array(file_source)
    elif suffix in SUFFIXES_WITH_DATAPATH:
        import h5py

        if subpath is None:
            dataset_path = DEFAULT_H5_DATASET_PATH
        else:
            dataset_path = str(subpath)

        reader = download(file_source)

        with h5py.File(reader, "r") as f:
            h5_dataset = f.get(  # pyright: ignore[reportUnknownVariableType]
                dataset_path
            )
            if not isinstance(h5_dataset, h5py.Dataset):
                raise ValueError(
                    f"{file_source} did not load as {h5py.Dataset}, but has type "
                    + str(
                        type(h5_dataset)  # pyright: ignore[reportUnknownArgumentType]
                    )
                )
            image: NDArray[Any]
            image = h5_dataset[:]  # pyright: ignore[reportUnknownVariableType]
    else:
        reader = download(file_source)

        image = imread(  # pyright: ignore[reportUnknownVariableType]
            reader.read(), extension=suffix
        )

    assert is_ndarray(image)
    return image


def split_dataset_path(
    source: _SourceT,
) -> Tuple[_SourceT, Suffix, Optional[PurePosixPath]]:
    """Split off subpath (e.g. internal  h5 dataset path)
    from a file path following a file extension.

    Examples:
        >>> _split_dataset_path(Path("my_file.h5/dataset"))
        (...Path('my_file.h5'), '.h5', PurePosixPath('dataset'))

        >>> _split_dataset_path(Path("my_plain_file"))
        (...Path('my_plain_file'), '', None)

    """
    if isinstance(source, RelativeFilePath):
        src = source.absolute()
    else:
        src = source

    del source

    def separate_pure_path(path: PurePosixPath):
        for p in path.parents:
            if p.suffix in SUFFIXES_WITH_DATAPATH:
                return p, p.suffix, PurePosixPath(path.relative_to(p))

        return path, path.suffix, None

    if isinstance(src, HttpUrl):
        file_path, suffix, data_path = separate_pure_path(PurePosixPath(src.path or ""))

        if data_path is None:
            return src, suffix, None

        return (
            HttpUrl(str(file_path).replace(f"/{data_path}", "")),
            suffix,
            data_path,
        )

    if isinstance(src, ZipPath):
        file_path, suffix, data_path = separate_pure_path(PurePosixPath(str(src)))

        if data_path is None:
            return src, suffix, None

        return (
            ZipPath(str(file_path).replace(f"/{data_path}", "")),
            suffix,
            data_path,
        )

    file_path, suffix, data_path = separate_pure_path(PurePosixPath(src))
    return Path(file_path), suffix, data_path


def get_suffix(source: Union[ZipPath, FileSource]) -> Suffix:
    if isinstance(source, Path):
        return source.suffix
    elif isinstance(source, ZipPath):
        return source.suffix
    if isinstance(source, RelativeFilePath):
        return source.path.suffix
    elif isinstance(source, ZipPath):
        return source.suffix
    elif isinstance(source, HttpUrl):
        if source.path is None:
            return ""
        else:
            return PurePosixPath(source.path).suffix
    else:
        assert_never(source)
