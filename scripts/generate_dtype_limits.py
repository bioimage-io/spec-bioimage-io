import numpy as np

dtype_limits = {}

for dtype in ["float32", "float64"]:
    info = np.finfo(dtype)
    dtype_limits[dtype] = (info.min, info.max)


for dtype in ["uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64", "int64"]:
    info = np.iinfo(dtype)
    dtype_limits[dtype] = (info.min, info.max)

print(dtype_limits)
