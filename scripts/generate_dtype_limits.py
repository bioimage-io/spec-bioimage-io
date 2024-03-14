from pprint import pprint
from typing import Dict, Tuple, Union

import numpy as np

dtype_limits: Dict[str, Tuple[Union[float, int], Union[float, int]]] = {}

for dtype in ["float32", "float64"]:
    info = np.finfo(dtype)
    dtype_limits[dtype] = (float(info.min), float(info.max))


for dtype in ["uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64"]:
    info = np.iinfo(dtype)
    dtype_limits[dtype] = (info.min, info.max)

if __name__ == "__main__":
    pprint(dtype_limits)
