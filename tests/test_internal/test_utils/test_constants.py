import re
from unittest import TestCase
from bioimageio.spec._internal._constants import SI_UNIT_REGEX


class TestSiUnitRegex(TestCase):
    def test_valid(self):
        for unit in ["lx·s", "kg/m^2·s^-2"]:
            with self.subTest(unit=unit):
                self.assertTrue(re.fullmatch(SI_UNIT_REGEX, unit))

    def test_invalid(self):
        for unit in ["lxs", " kg"]:
            with self.subTest(unit=unit):
                self.assertFalse(re.fullmatch(SI_UNIT_REGEX, unit))
