from typing import TypeVar

from ._generated_spdx_license_literals import (
    DeprecatedLicenseId as DeprecatedLicenseIdLiteral,
)
from ._generated_spdx_license_literals import LicenseId as LicenseIdLiteral
from .validated_string import ValidatedString

LicenceT = TypeVar("LicenceT", LicenseIdLiteral, DeprecatedLicenseIdLiteral)


class _LicenseId(ValidatedString[LicenceT], frozen=True):
    def __repr__(self):
        # don't include full literal in class repr
        name, *_ = self.__class__.__name__.split("[")
        return f'{name}("{self.root}")'


class DeprecatedLicenseId(_LicenseId[DeprecatedLicenseIdLiteral], frozen=True):
    pass


class LicenseId(_LicenseId[LicenseIdLiteral], frozen=True):
    pass
