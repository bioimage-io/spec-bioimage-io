from typing import TypeVar

from bioimageio.spec._internal._generated_spdx_license_literals import (
    DeprecatedLicenseId as DeprecatedLicenseIdLiteral,
)
from bioimageio.spec._internal._generated_spdx_license_literals import (
    LicenseId as LicenseIdLiteral,
)
from bioimageio.spec._internal.validated_string import ValidatedString

L = TypeVar("L", LicenseIdLiteral, DeprecatedLicenseIdLiteral)


class _LicenseId(ValidatedString[L]):
    def __repr__(self):
        # don't include full literal in class repr
        name, *_ = self.__class__.__name__.split("[")
        return f'{name}("{self.root}")'


class DeprecatedLicenseId(_LicenseId[DeprecatedLicenseIdLiteral]):
    pass


class LicenseId(_LicenseId[LicenseIdLiteral]):
    pass
