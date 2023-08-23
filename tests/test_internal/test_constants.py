import logging
import re
from unittest import TestCase

from bioimageio.spec._internal.constants import ALERT, INFO, SI_UNIT_REGEX, WARNING


class TestSiUnitRegex(TestCase):
    def test_valid(self):
        for unit in ["lx·s", "kg/m^2·s^-2"]:
            with self.subTest(unit=unit):
                self.assertTrue(re.fullmatch(SI_UNIT_REGEX, unit))

    def test_invalid(self):
        for unit in ["lxs", " kg", "kg/m^-2"]:
            with self.subTest(unit=unit):
                self.assertFalse(re.fullmatch(SI_UNIT_REGEX, unit))


class TestConstants(TestCase):
    def test_warning_levels(self):
        """test that our warning levels nicely match python's logging module's levels"""
        self.assertLess(ALERT, logging.ERROR, "ALERT < logging.ERROR")
        self.assertGreater(ALERT, logging.WARNING, "ALERT > logging.WARNING")
        self.assertEqual(WARNING, logging.WARNING, "WARNING == logging.WARNING")
        self.assertEqual(INFO, logging.INFO, "INFO == logging.INFO")
