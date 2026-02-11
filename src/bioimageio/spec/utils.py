"""Utility functions for bioimage.io specifications (mostly IO)."""

import json
from typing import Any, Dict, List, TypedDict, Union

from imageio.v3 import imread  # pyright: ignore[reportUnknownVariableType]
from numpy.typing import NDArray

from ._description import ensure_description_is_dataset as ensure_description_is_dataset
from ._description import ensure_description_is_model as ensure_description_is_model
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


def load_image(source: Union[FileDescr, ZipPath, PermissiveFileSource]) -> NDArray[Any]:
    """load a single image as numpy array

    Args:
        source: image source
    """

    if isinstance(source, (FileDescr, ZipPath)):
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
