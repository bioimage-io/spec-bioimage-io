"""Utility functions for bioimage.io specifications (mostly IO)."""

from __future__ import annotations

import json
import shutil
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict, overload

from imageio.v3 import imread  # pyright: ignore[reportUnknownVariableType]
from loguru import logger
from numpy.typing import NDArray

from ._description import ensure_description_is_dataset as ensure_description_is_dataset
from ._description import ensure_description_is_model as ensure_description_is_model
from ._internal._settings import settings
from ._internal.io import FileDescr
from ._internal.io import download as download
from ._internal.io import extract_file_name as extract_file_name
from ._internal.io import get_reader as get_reader
from ._internal.io import get_sha256 as get_sha256
from ._internal.io import (
    identify_bioimageio_yaml_file_name as identify_bioimageio_yaml_file_name,
)
from ._internal.io import interprete_file_source as interprete_file_source
from ._internal.io import is_valid_bioimageio_yaml_name as is_valid_bioimageio_yaml_name
from ._internal.io_basics import ZipPath
from ._internal.io_utils import load_array as load_array
from ._internal.io_utils import open_bioimageio_yaml as open_bioimageio_yaml
from ._internal.io_utils import read_yaml as read_yaml
from ._internal.io_utils import save_array as save_array
from ._internal.io_utils import write_yaml as write_yaml
from ._internal.type_guards import is_ndarray
from ._internal.types import PermissiveFileSource, RelativeFilePath
from ._internal.utils import files
from ._utils_zarr import open_zarr_multiscale_array

if TYPE_CHECKING:
    import dask.array

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
    licenses: list[SpdxLicenseEntry]
    releaseDate: str


def get_spdx_licenses() -> SpdxLicenses:
    """get details of the SPDX licenses known to bioimageio.spec"""
    with (
        files("bioimageio.spec")
        .joinpath("static/spdx_licenses.json")
        .open("r", encoding="utf-8")
    ) as f:
        return json.load(f)


def get_bioimageio_json_schema() -> dict[str, Any]:
    """get the bioimageio specification as a JSON schema"""
    with (
        files("bioimageio.spec")
        .joinpath("static/bioimageio_schema.json")
        .open("r", encoding="utf-8")
    ) as f:
        return json.load(f)


@dataclass
class ImageMeta:
    axes: Sequence[str] | None = None


@overload
def load_image(
    source: FileDescr | ZipPath | PermissiveFileSource,
    *,
    return_image_meta: Literal[False] = False,
) -> NDArray[Any] | dask.array.Array: ...


@overload
def load_image(
    source: FileDescr | ZipPath | PermissiveFileSource,
    *,
    return_image_meta: Literal[True],
) -> tuple[NDArray[Any] | dask.array.Array, ImageMeta]: ...


def load_image(
    source: FileDescr | ZipPath | PermissiveFileSource,
    *,
    return_image_meta: bool = False,
) -> (
    NDArray[Any] | dask.array.Array | tuple[NDArray[Any] | dask.array.Array, ImageMeta]
):
    """load a single image as numpy array

    Args:
        source: image source
    """

    source = _interprete_file_source(source)

    if source.suffix == ".npy":
        image = load_array(source)
        meta = ImageMeta(axes=None)
    else:
        try:
            reader = get_reader(source)
            image = imread(reader.read(), extension=source.suffix)
        except Exception:
            image, meta = _load_zarr_image(source)
        else:
            meta = ImageMeta(axes=None)
            assert is_ndarray(image)

    if return_image_meta:
        return image, meta
    else:
        return image


def _load_zarr_image(
    source: FileDescr | PermissiveFileSource,
) -> tuple[NDArray[Any] | dask.array.Array, ImageMeta]:
    """load a single image as numpy array

    Args:
        source: image source
    """
    import dask.array as da

    source = _interprete_file_source(source)
    if isinstance(source, FileDescr):
        source = source.source.absolute()

    if isinstance(source, ZipPath):
        raise NotImplementedError(
            "Loading zarr images from zip files is not implemented."
        )

    array, ms = open_zarr_multiscale_array(
        source.as_posix() if isinstance(source, Path) else str(source)
    )
    image = da.from_zarr(array)
    axes = tuple(str(a) for a in ms.axes())
    return image, ImageMeta(axes=axes)


def _interprete_file_source(source: FileDescr | ZipPath | PermissiveFileSource):
    if isinstance(source, (FileDescr, ZipPath)):
        parsed_source = source
    else:
        parsed_source = interprete_file_source(source)
        if isinstance(parsed_source, RelativeFilePath):
            parsed_source = parsed_source.absolute()

    return parsed_source


def empty_cache():
    """Empty the bioimageio disk cache."""

    shutil.rmtree(settings.cache_path)
    settings.cache_path.mkdir(parents=True, exist_ok=True)
    logger.info("Emptied cache at {}", settings.cache_path)
