import json
from typing import List, TypedDict

from ._description import ensure_description_is_dataset as ensure_description_is_dataset
from ._description import ensure_description_is_model as ensure_description_is_model
from ._internal.io import download as download
from ._internal.io import extract_file_name as extract_file_name
from ._internal.io import get_sha256 as get_sha256
from ._internal.io import (
    identify_bioimageio_yaml_file_name as identify_bioimageio_yaml_file_name,
)
from ._internal.io import is_valid_bioimageio_yaml_name as is_valid_bioimageio_yaml_name
from ._internal.io_utils import load_array as load_array
from ._internal.io_utils import save_array as save_array
from ._internal.utils import files


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
