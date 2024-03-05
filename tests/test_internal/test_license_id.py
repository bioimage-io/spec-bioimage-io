import pytest
from pydantic import ValidationError


def test_license_id():
    from bioimageio.spec._internal.license_id import LicenseId

    _ = LicenseId("MIT")

    with pytest.raises(ValidationError):
        _ = LicenseId("not_a_valid_license_id")  # pyright: ignore[reportArgumentType]


def test_deprecated_license_id():
    from bioimageio.spec._internal.license_id import DeprecatedLicenseId

    _ = DeprecatedLicenseId("AGPL-1.0")

    with pytest.raises(ValidationError):
        _ = DeprecatedLicenseId(
            "not_a_valid_license_id"  # pyright: ignore[reportArgumentType]
        )
