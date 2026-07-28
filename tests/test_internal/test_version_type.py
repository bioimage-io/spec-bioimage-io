from __future__ import annotations

import pytest

from tests.utils import check_type


@pytest.mark.parametrize(
    "value", [1, "1", 0.1, 1.0, "1.0", "0.0.1", "0.1.0", "0.1.1", "1.0.0", "1.1.1"]
)
def test_version_type(value: str | float):
    from bioimageio.spec._internal.version_type import Version

    check_type(
        Version,
        value,
        expected_root=value,
        expected_deserialized=value,
    )
