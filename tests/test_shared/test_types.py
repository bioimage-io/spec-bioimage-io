from unittest import TestCase

from bioimageio.spec.shared.types import SiUnit
from tests.unittest_utils import BaseTestCases


class TestRelativePath(TestCase):
    def test_eq(self):
        from bioimageio.spec.shared.types import RelativePath

        p = RelativePath(__file__)
        p2 = RelativePath(__file__)
        self.assertEqual(p, p2)


class TestSiUnit(BaseTestCases.TestType):
    type_ = SiUnit
    valid = ("lx·s", "kg/m^2·s^-2")
    invalid = ["lxs", " kg"]
