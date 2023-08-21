import collections.abc
from typing import Any
from unittest import TestCase

from bioimageio.spec._internal.base_nodes import FrozenDictNode, Kwargs


class TestFrozenDict(TestCase):
    empty = FrozenDictNode[Any, Any]()
    lala = Kwargs(lala=3)  # type: ignore

    def test_is_mapping(self):
        self.assertIsInstance(self.empty, collections.abc.Mapping)
        self.assertIsInstance(self.lala, collections.abc.Mapping)

    def test_get(self):
        self.assertEqual(self.lala.get("lala"), 3)
        self.assertIs(self.empty.get("lala"), None)

    def test_bool(self):
        self.assertTrue(bool(self.lala))
        self.assertFalse(bool(self.empty))
