from pydantic import RootModel

from ._generated_spdx_license_literals import (
    DeprecatedLicenseId as DeprecatedLicenseIdLiteral,
)
from ._generated_spdx_license_literals import LicenseId as LicenseIdLiteral
from .validated_string import ValidatedString


class LicenseId(ValidatedString):
    root_model = RootModel[LicenseIdLiteral]


class DeprecatedLicenseId(ValidatedString):
    root_model = RootModel[DeprecatedLicenseIdLiteral]
