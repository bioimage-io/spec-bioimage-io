import json
from typing import List, TypedDict

from ._description import ensure_description_is_dataset, ensure_description_is_model
from ._internal.io import (
    download,
    extract_file_name,
    get_sha256,
    identify_bioimageio_yaml_file_name,
    is_valid_bioimageio_yaml_name,
)
from ._internal.io_utils import load_array, save_array
from ._internal.utils import files

__all__ = [
    "download",
    "ensure_description_is_dataset",
    "ensure_description_is_model",
    "extract_file_name",
    "get_sha256",
    "get_spdx_licenses",
    "identify_bioimageio_yaml_file_name",
    "is_valid_bioimageio_yaml_name",
    "load_array",
    "save_array",
    "SpdxLicenseEntry",
    "SpdxLicenses",
]


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
    with files("bioimageio.spec").joinpath("static/spdx_licenses.json").open(
        "r", encoding="utf-8"
    ) as f:
        return json.load(f)
