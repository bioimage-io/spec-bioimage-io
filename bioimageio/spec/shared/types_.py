from __future__ import annotations
from typing import Annotated, Union
from collections.abc import Mapping, Sequence, Callable
from pydantic import AfterValidator

RawLeafValue = Union[int, float, str, bool, None]
RawMapping = Mapping[str, "RawValue"]
RawSequence = Sequence["RawValue"]
RawValue = Union[RawLeafValue, RawSequence, RawMapping]

RawDataConverter = Callable[[RawMapping], RawMapping]
RawDict = dict[str, RawValue]

CapitalStr = Annotated[str, AfterValidator()