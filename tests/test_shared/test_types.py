from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from bioimageio.spec._internal.types import Datetime, SiUnit
from bioimageio.spec._internal.types._file_source import RelativePath
from tests.utils import check_type


@pytest.mark.parametrize("path", ["a.test", "there/b", "./here/or/there/c"])
def test_relative_path(path: str):
    p = RelativePath(path)
    p2 = RelativePath(Path(path))
    assert p == p2
    p3 = RelativePath(Path(path).as_posix())
    assert p == p3

    with pytest.raises(ValueError):
        _ = RelativePath(Path(path).absolute())

    with pytest.raises(ValueError):
        _ = RelativePath(str(Path(path).absolute()))

    with pytest.raises(ValueError):
        _ = RelativePath(Path(path).absolute().as_posix())


@pytest.mark.parametrize("value", ["lx·s", "kg/m^2·s^-2"])
def test_si_unit(value: str):
    check_type(SiUnit, value)


@pytest.mark.parametrize("value", ["lxs", " kg"])
def test_si_unit_invalid(value: str):
    check_type(SiUnit, value, is_invalid=True)


NOW = datetime.now()


@pytest.mark.parametrize(
    "value,expected",
    [
        (
            "2019-12-11T12:22:32+00:00",
            datetime.fromisoformat("2019-12-11T12:22:32+00:00"),
        ),
        (
            "2019-12-11T12:22:32+00:00",
            datetime(2019, 12, 11, 12, 22, 32, tzinfo=timezone.utc),
        ),
        ("2019-12-11T12:22:32Z", datetime.fromisoformat("2019-12-11T12:22:32+00:00")),
        (
            "2019-12-11T12:22:32Z",
            datetime(2019, 12, 11, 12, 22, 32, tzinfo=timezone.utc),
        ),
        (NOW, NOW),
    ],
)
def test_datetime(value: Any, expected: Any):
    check_type(Datetime, value, expected=expected)


@pytest.mark.parametrize(
    "value",
    [
        "2019-12-11T12:22:32+00/00",
        "2019-12-11T12:22:32Y",
        "2019-12-11T12:22:32Zulu",
        "201912-11T12:22:32+00:00",
        "NOW",
    ],
)
def test_datetime_invalid(value: Any):
    check_type(Datetime, value, is_invalid=True)
