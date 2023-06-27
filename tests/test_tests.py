from pathlib import Path
from typing import Iterable
import unittest


class TestDebugValues(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        loader = unittest.TestLoader()
        self.suite = loader.discover(str(Path(__file__).parent), top_level_dir=str(Path(__file__).parent.parent))

    def test(self):
        for s in self.yield_test_cases(self.suite):
            with self.subTest(s.__class__.__name__):
                for attr in dir(s):
                    if attr.startswith("DEBUG"):
                        debug_value = getattr(s, attr)
                        self.assertIsNone(debug_value, f"{s}.{attr}")

    @classmethod
    def yield_test_cases(cls, s: unittest.TestSuite) -> Iterable[unittest.TestCase]:
        for ss in s:
            if isinstance(ss, unittest.TestSuite):
                yield from cls.yield_test_cases(ss)
            elif ss.__class__.__name__ != "TestDebugValues":
                yield ss
