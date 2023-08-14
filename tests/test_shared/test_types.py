from datetime import datetime, timezone
from unittest import TestCase

from bioimageio.spec.shared.types import Datetime, SiUnit
from tests.unittest_utils import TestBases, TypeSubTest


class TestRelativePath(TestCase):
    def test_eq(self):
        from bioimageio.spec.shared.types import RelativePath

        p = RelativePath(__file__)
        p2 = RelativePath(__file__)
        self.assertEqual(p, p2)


class TestSiUnit(TestBases.TestType):
    type_ = SiUnit
    valid = ("lx·s", "kg/m^2·s^-2")
    invalid = ["lxs", " kg"]


NOW = datetime.now()


class TestDateTime(TestBases.TestType):
    type_ = Datetime
    valid = (
        TypeSubTest("2019-12-11T12:22:32+00:00", datetime.fromisoformat("2019-12-11T12:22:32+00:00")),
        TypeSubTest("2019-12-11T12:22:32+00:00", datetime(2019, 12, 11, 12, 22, 32, tzinfo=timezone.utc)),
        TypeSubTest("2019-12-11T12:22:32Z", datetime.fromisoformat("2019-12-11T12:22:32+00:00")),
        TypeSubTest("2019-12-11T12:22:32Z", datetime(2019, 12, 11, 12, 22, 32, tzinfo=timezone.utc)),
        TypeSubTest(NOW, NOW),
    )
    invalid = (
        "2019-12-11T12:22:32+0000",
        "2019-12-11T12:22:32Y",
        "2019-12-11T12:22:32Zulu",
        "201912-11T12:22:32+00:00",
        "NOW",
    )
