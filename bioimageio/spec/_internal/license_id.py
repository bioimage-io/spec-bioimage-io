from typing import Any, ClassVar, Type

from pydantic import RootModel

from ._generated_spdx_license_literals import (
    DeprecatedLicenseId as DeprecatedLicenseIdLiteral,
)
from ._generated_spdx_license_literals import LicenseId as LicenseIdLiteral
from .validated_string import ValidatedString

__all__ = [
    "DeprecatedLicenseId",
    "DeprecatedLicenseIdLiteral",
    "LicenseId",
    "LicenseIdLiteral",
]


class LicenseId(ValidatedString):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[LicenseIdLiteral]


class DeprecatedLicenseId(ValidatedString):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[DeprecatedLicenseIdLiteral]
