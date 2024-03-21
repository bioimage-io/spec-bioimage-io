from typing import Union

import pytest
from pydantic import BaseModel, Field, ValidationError


def test_license_id():
    from bioimageio.spec._internal.license_id import LicenseId

    _ = LicenseId("MIT")

    with pytest.raises(ValidationError):
        _ = LicenseId("not_a_valid_license_id")


def test_license_id_in_model():
    """pydantic 2 now defaults to smart unions, which try to find the best match,
    somehow `str` is considered a better match than a valid `LicneseId`, so we should
    only use 'left_to_right' unions with `RootModel[str]`, e.g. `ValidatedString`"""
    from bioimageio.spec._internal.license_id import LicenseId

    class Model(BaseModel):
        lid: Union[LicenseId, str] = Field(union_mode="left_to_right")

    out = Model.model_validate({"lid": "CC-BY-4.0"}).lid
    assert isinstance(out, LicenseId)


def test_deprecated_license_id():
    from bioimageio.spec._internal.license_id import DeprecatedLicenseId

    _ = DeprecatedLicenseId("AGPL-1.0")

    with pytest.raises(ValidationError):
        _ = DeprecatedLicenseId("not_a_valid_license_id")
