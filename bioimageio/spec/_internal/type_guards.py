import collections.abc
from typing import Any, Mapping, Sequence

from typing_extensions import TypeGuard


def is_sequence(v: Any) -> TypeGuard[Sequence[Any]]:
    """to avoid Sequence[Unknown]"""
    return isinstance(v, collections.abc.Sequence)


def is_mapping(v: Any) -> TypeGuard[Mapping[Any, Any]]:
    """to avoid Mapping[Unknown, Unknown]"""
    return isinstance(v, collections.abc.Mapping)
