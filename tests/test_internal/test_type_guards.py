from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import pytest
from typing_extensions import assert_type

from bioimageio.spec._internal.type_guards import (
    is_dict,
    is_kwargs,
    is_list,
    is_mapping,
    is_ndarray,
    is_sequence,
    is_set,
    is_tuple,
)


def test_type_guards():
    assert is_dict({})
    assert not is_dict([])
    assert is_set(set())
    assert not is_set({})
    assert is_mapping({"key": "value"})
    assert not is_mapping([])
    assert is_sequence(["value"])
    assert is_sequence("value")
    assert not is_sequence({})
    assert is_tuple(("value",))
    assert not is_tuple(["value"])
    assert is_list(["value"])
    assert not is_list(("value",))
    assert is_ndarray(np.array([1]))
    assert not is_ndarray([1])


@pytest.mark.parametrize(
    "value, expected",
    [
        ({}, True),
        ({"name": "value"}, True),
        ({1: "value"}, False),
    ],
)
def test_is_kwargs(value: Mapping[Any, str], expected: bool):
    assert is_kwargs(value) is expected


def test_narrowed_types() -> None:
    mapping: Mapping[str, int] = {"value": 1}
    sequence: Sequence[int] = [1]

    if is_mapping(mapping):
        _ = assert_type(mapping, Mapping[str, int])
    if is_sequence(sequence):
        _ = assert_type(sequence, Sequence[int])
