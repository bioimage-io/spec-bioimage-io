from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, List, Sequence, Tuple, Union

import imageio
import numpy as np
from numpy.typing import NDArray

from bioimageio.spec.model.v0_5 import (
    AnyAxis,
    BatchAxis,
    ChannelAxis,
    IndexAxis,
    InputTensorDescr,
    OutputTensorDescr,
    SpaceInputAxis,
    SpaceOutputAxis,
    TimeInputAxis,
    TimeOutputAxis,
)


def squeeze(data: NDArray[Any], axes: Sequence[AnyAxis]) -> Tuple[NDArray[Any], List[AnyAxis]]:
    """apply numpy.ndarray.squeeze while keeping track of the axis descriptions remaining"""
    if data.ndim != len(axes):
        raise ValueError(f"tensor shape {data.shape} does not match described axes {[a.id for a in axes]}")

    axes = [deepcopy(a) for a, s in zip(axes, data.shape) if s != 1]
    return data.squeeze(), axes


def normalize(data: NDArray[Any], axis: Union[int, Sequence[int], None], eps: float = 1e-7) -> NDArray[np.float32]:
    data = data.astype("float32")
    data -= data.min(axis=axis, keepdims=True)
    data /= data.max(axis=axis, keepdims=True) + eps
    return data


def to_2d_image(data: NDArray[Any], axes: Sequence[AnyAxis]):
    data, axes = squeeze(data, axes)

    # take slice fom any batch or index axis if needed
    # and convert the first channel axis and take a slice from any additional channel axes
    slices: Tuple[slice, ...] = ()
    ndim = data.ndim
    ndim_need = 3 if any(isinstance(a, ChannelAxis) for a in axes) else 2
    has_c_axis = False
    for i, a in enumerate(axes):
        s = data.shape[i]
        assert s > 1
        if isinstance(a, (BatchAxis, IndexAxis)) and ndim > ndim_need:
            data = data[slices + (slice(s // 2 - 1, s // 2),)]
            ndim -= 1
        elif isinstance(a, ChannelAxis):
            if has_c_axis:
                # second channel axis
                data = data[slices + (slice(0, 1),)]
                ndim -= 1
            else:
                has_c_axis = True
                if s == 2:
                    data = np.concatenate(
                        [
                            data[slices + (slice(1, 2),)],
                            data[slices + (slice(0, 1),)],
                            (data[slices + (slice(0, 1),)] + data[slices + (slice(1, 2),)]) / 2,
                        ],
                        axis=i,
                    )
                elif data.shape[i] == 3:
                    pass
                else:
                    data = data[slices + (slice(3),)]

                assert data.shape[i] == 3

        slices += (slice(None),)

    data, axes = squeeze(data, axes)

    # take slice from z axis if needed
    slices = ()
    if ndim > ndim_need:
        for i, a in enumerate(axes):
            s = data.shape[i]
            if a.id == "z":
                data = data[slices + (slice(s // 2 - 1, s // 2),)]
                data, axes = squeeze(data, axes)
                ndim -= 1
                break

        slices += (slice(None),)

    # take slice from any space or time axis
    slices = ()

    for i, a in enumerate(axes):
        if ndim <= ndim_need:
            break

        s = data.shape[i]
        assert s > 1
        if isinstance(a, (SpaceInputAxis, SpaceOutputAxis, TimeInputAxis, TimeOutputAxis)):
            data = data[slices + (slice(s // 2 - 1, s // 2),)]
            ndim -= 1

        slices += (slice(None),)

    del slices
    data, axes = squeeze(data, axes)

    norm_along = [i for i, a in enumerate(axes) if a.type in ("space", "time")] or None
    # normalize the data and map to 8 bit
    data = normalize(data, norm_along)
    data = (data * 255).astype("uint8")

    if has_c_axis:
        axes_order = [0, 1, 2]
        c = [i for i in range(3) if isinstance(axes[i], ChannelAxis)][0]
        axes_order.append(axes_order.pop(c))
        axes = [axes[ao] for ao in axes_order]
        data = data.transpose(axes_order)
    else:
        data = np.repeat(data[:, :, None], 3, axis=2)

    if data.ndim != 3 or data.shape[0] != 3 or data.shape[1] < 10 or data.shape[2] < 10:
        raise ValueError("Failed to construct cover image")

    return data


def create_diagonal_split_image(im0: NDArray[Any], im1: NDArray[Any]):
    assert im0.dtype == im1.dtype == np.uint8
    assert im0.shape == im1.shape
    assert im0.ndim == 3
    N, M, C = im0.shape
    assert C == 3
    out = np.ones((N, M, C), dtype="uint8")
    for c in range(C):
        outc = np.tril(im0[..., c])
        mask = outc == 0
        outc[mask] = np.triu(im1[..., c])[mask]
        out[..., c] = outc

    return out


# create better cover images for 3d data and non-image outputs
def generate_covers(
    inputs: Sequence[Tuple[InputTensorDescr, NDArray[Any]]], outputs: Sequence[Tuple[OutputTensorDescr, NDArray[Any]]]
) -> List[Path]:
    ipt_descr, ipt = inputs[0]
    out_descr, out = outputs[0]

    ipt_img = to_2d_image(ipt, ipt_descr.axes)
    out_img = to_2d_image(out, out_descr.axes)

    cover_folder = Path(str(TemporaryDirectory()))
    if ipt_img.shape == out_img.shape:
        covers = [cover_folder / "cover.png"]
        imageio.imwrite(covers[0], create_diagonal_split_image(ipt_img, out_img))
    else:
        covers = [cover_folder / "input.png", cover_folder / "output.png"]
        imageio.imwrite(covers[0], ipt_img)
        imageio.imwrite(covers[1], out_img)

    return covers
