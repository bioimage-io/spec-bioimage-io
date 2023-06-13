from __future__ import annotations
from typing import Union
from collections.abc import Mapping, Sequence, Callable

RawLeafValue = Union[int, float, str, bool, None]
RawMapping = Mapping[str, "RawValue"]
RawSequence = Sequence["RawValue"]
RawValue = Union[RawLeafValue, RawSequence, RawMapping]

RawDataConverter = Callable[[RawMapping], RawMapping]
