import logging
from unittest import TestCase

from bioimageio.spec._internal._warn import ALERT, INFO, WARNING


class TestWarnings(TestCase):
    def test_levels(self):
        """test that our warning levels nicely match python's logging module's levels"""
        self.assertLess(ALERT, logging.ERROR)
        self.assertGreater(ALERT, logging.WARNING)
        self.assertEqual(WARNING, logging.WARNING)
        self.assertEqual(INFO, logging.INFO)
