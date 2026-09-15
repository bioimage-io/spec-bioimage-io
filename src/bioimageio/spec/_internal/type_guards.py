"""use these type guards with caution!
They widen the type to T[Any], which is not always correct."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Hashable, TypeVar

import numpy as np
from numpy.typing import NDArray
from typing_extensions import TypeGuard

T = TypeVar("T")
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


def is_dict(v: Any | Mapping[K, V]) -> TypeGuard[dict[K, V]]:
    """to avoid Dict[Unknown, Unknown]"""
    return isinstance(v, dict)


def is_set(v: Any) -> TypeGuard[set[Any]]:
    """to avoid Set[Unknown]"""
    return isinstance(v, set)


def is_kwargs(v: Any | Mapping[Any, T]) -> TypeGuard[Mapping[str, T]]:
    return isinstance(v, Mapping) and all(
        isinstance(k, str)
        for k in v  # pyright: ignore[reportUnknownVariableType]
    )


def is_mapping(v: Any | Mapping[K, V]) -> TypeGuard[Mapping[K, V]]:
    """to avoid Mapping[Unknown, Unknown]"""
    return isinstance(v, Mapping)


def is_sequence(v: Any | Sequence[T]) -> TypeGuard[Sequence[T]]:
    """to avoid Sequence[Unknown]"""
    return isinstance(v, Sequence)


def is_tuple(v: Any | Sequence[T]) -> TypeGuard[tuple[T, ...]]:
    """to avoid Tuple[Unknown, ...]"""
    return isinstance(v, tuple)


def is_list(v: Any) -> TypeGuard[list[Any]]:
    """to avoid List[Unknown]"""
    return isinstance(v, list)


def is_ndarray(v: Any) -> TypeGuard[NDArray[Any]]:
    return isinstance(v, np.ndarray)
