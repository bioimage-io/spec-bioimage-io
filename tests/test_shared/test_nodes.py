import collections.abc
from unittest import TestCase

from bioimageio.spec.shared.nodes import FrozenDictNode


class TestFrozenDict(TestCase):
    def test_is_mapping(self):
        d = FrozenDictNode()
        self.assertIsInstance(d, collections.abc.Mapping)
