import collections.abc
from typing import Any, Dict, List, Mapping, Sequence, Tuple

import numpy as np
from numpy.typing import NDArray
from typing_extensions import TypeGuard


def is_dict(v: Any) -> TypeGuard[Dict[Any, Any]]:
    """to avoid Dict[Unknown, Unknown]"""
    return isinstance(v, dict)


def is_kwargs(v: Any) -> TypeGuard[Dict[str, Any]]:
    return isinstance(v, dict) and all(
        isinstance(k, str) for k in v  # pyright: ignore[reportUnknownVariableType]
    )


def is_mapping(v: Any) -> TypeGuard[Mapping[Any, Any]]:
    """to avoid Mapping[Unknown, Unknown]"""
    return isinstance(v, collections.abc.Mapping)


def is_sequence(v: Any) -> TypeGuard[Sequence[Any]]:
    """to avoid Sequence[Unknown]"""
    return isinstance(v, collections.abc.Sequence)


def is_tuple(v: Any) -> TypeGuard[Tuple[Any, ...]]:
    """to avoid Tuple[Unknown, ...]"""
    return isinstance(v, tuple)


def is_list(v: Any) -> TypeGuard[List[Any]]:
    """to avoid List[Unknown]"""
    return isinstance(v, list)


def is_ndarray(v: Any) -> TypeGuard[NDArray[Any]]:
    return isinstance(v, np.ndarray)
