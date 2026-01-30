"""Utility functions for bioimage.io specifications (mostly IO)."""

import json
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

from imageio.v3 import imread  # pyright: ignore[reportUnknownVariableType]
from numpy.typing import NDArray
from typing_extensions import assert_never

from ._description import ensure_description_is_dataset, ensure_description_is_model
from ._internal.io import (
    FileDescr,
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
from ._internal.types import PermissiveFileSource, RelativeFilePath
from ._internal.url import HttpUrl
from ._internal.utils import files

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
        parsed_source = parsed_source.absolute()

    if parsed_source.suffix == ".npy":
        image = load_array(parsed_source)
    else:
        reader = get_reader(parsed_source)
        image = imread(  # pyright: ignore[reportUnknownVariableType]
            reader.read(), extension=parsed_source.suffix
        )

    assert is_ndarray(image)
    return image
