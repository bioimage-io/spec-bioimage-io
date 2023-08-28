import collections.abc
from typing import Any

import pytest

from bioimageio.spec._internal.base_nodes import FrozenDictNode, Kwargs


@pytest.fixture
def empty():
    return FrozenDictNode[Any, Any]()


@pytest.fixture
def lala():
    return Kwargs(lala=3)  # type: ignore


def test_is_mapping(empty: FrozenDictNode[Any, Any], lala: Kwargs):
    assert isinstance(empty, collections.abc.Mapping)
    assert isinstance(lala, collections.abc.Mapping)


def test_get(empty: FrozenDictNode[Any, Any], lala: Kwargs):
    assert lala.get("lala") == 3
    assert empty.get("lala") is None


def test_bool(empty: FrozenDictNode[Any, Any], lala: Kwargs):
    assert bool(lala)
    assert not empty
