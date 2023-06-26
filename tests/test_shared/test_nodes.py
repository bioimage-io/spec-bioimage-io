import collections.abc
from unittest import TestCase

from bioimageio.spec.shared.nodes import FrozenDictNode


class TestFrozenDict(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.empty = FrozenDictNode()
        self.lala = FrozenDictNode(lala=3)  # type: ignore

    def test_is_mapping(self):
        self.assertIsInstance(self.empty, collections.abc.Mapping)
        self.assertIsInstance(self.lala, collections.abc.Mapping)

    def test_get(self):
        self.assertEqual(self.lala.get("lala"), 3)
        self.assertIs(self.empty.get("lala"), None)

    def test_bool(self):
        self.assertTrue(bool(self.lala))
        self.assertFalse(bool(self.empty))
