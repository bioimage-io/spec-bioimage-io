from typing import Mapping, Sequence
from typing import Union

RawLeafValue = Union[int, float, str, bool, None]
RawMapping = Mapping[str, "RawValue"]
RawSequence = Sequence["RawValue"]
RawValue = Union[RawLeafValue, RawSequence, RawMapping]

# RawDict = dict[str, RawValue]  # we often are interested in shallow manipulaiton of dict(<RawMapping>)
