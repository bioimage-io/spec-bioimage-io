"""
Built-in custom op: cellpose_flow_dynamics
==========================================

Decodes Cellpose / Cellpose-SAM model outputs into instance label images
using flow-dynamics integration and connected-component labelling.

Usage in rdf.yaml
-----------------
::

    postprocessing:
      - id: custom
        callable: cellpose_flow_dynamics
        kwargs:
          cellprob_threshold: 0.0   # optional — default shown
          flow_threshold: 0.4       # optional — default shown

Expected model outputs (in rdf.yaml declaration order):
  - flow_y   : vertical flow field (H x W), float32
  - flow_x   : horizontal flow field (H x W), float32
  - cellprob : cell probability map (H x W), float32, sigmoid-activated

Returns:
  - labels   : instance label image (H x W), int32
    0 = background, 1..N = object instances

References
----------
Stringer et al. (2021) "Cellpose: a generalist algorithm for cellular
segmentation." Nature Methods 18, 100–106.
https://doi.org/10.1038/s41592-020-01018-x

Pachitariu & Stringer (2022) "Cellpose 2.0: how to train your own model."
Nature Methods 19, 1634–1641.
https://doi.org/10.1038/s41592-022-01663-4
"""

from typing import Callable

import numpy as np


def cellpose_flow_dynamics(
    cellprob_threshold: float = 0.0,
    flow_threshold: float = 0.4,
    interp: bool = True,
    do_3D: bool = False,
) -> Callable[..., np.ndarray]:
    """Factory for Cellpose flow-dynamics postprocessing.

    Args:
        cellprob_threshold: Pixels with cell probability above this value
            are candidates for mask generation. Default: 0.0.
        flow_threshold: Maximum allowed flow error for each mask candidate.
            Masks with higher error are discarded. Default: 0.4.
        interp: Interpolate flows during dynamics integration. Default: True.
        do_3D: Process volumetric (Z, Y, X) inputs. Default: False.

    Returns:
        A function ``run(flow_y, flow_x, cellprob) -> labels`` that produces
        an integer label image from Cellpose model outputs.
    """

    def run(*arrays: np.ndarray) -> np.ndarray:
        """Process Cellpose outputs into instance labels.

        Args:
            *arrays: Model output tensors in declaration order:
                arrays[0] = flow_y  (vertical flow field)
                arrays[1] = flow_x  (horizontal flow field)
                arrays[2] = cellprob (cell probability, sigmoid-activated)

        Returns:
            Integer label image (same H x W as input). 0 = background.
        """
        if len(arrays) < 3:
            raise ValueError(
                f"cellpose_flow_dynamics expects 3 output tensors "
                f"(flow_y, flow_x, cellprob), got {len(arrays)}."
            )

        flow_y, flow_x, cellprob = arrays[0], arrays[1], arrays[2]

        try:
            from cellpose import dynamics
        except ImportError as e:
            raise ImportError(
                "cellpose is required for cellpose_flow_dynamics. "
                "Install with: pip install cellpose"
            ) from e

        flows = np.stack([flow_y, flow_x], axis=0)  # (2, H, W)
        masks, *_ = dynamics.compute_masks(
            flows,
            cellprob,
            cellprob_threshold=cellprob_threshold,
            flow_threshold=flow_threshold,
            interp=interp,
            do_3D=do_3D,
        )
        return masks.astype(np.int32)

    return run
