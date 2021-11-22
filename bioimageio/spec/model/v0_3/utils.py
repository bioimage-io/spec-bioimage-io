from copy import deepcopy
from typing import Optional, Sequence

from . import raw_nodes


def filter_resource_description(
    raw_rd: raw_nodes.Model, weights_priority_order: Optional[Sequence[raw_nodes.WeightsFormat]] = None
) -> raw_nodes.Model:
    # filter weights
    raw_rd = deepcopy(raw_rd)
    if weights_priority_order is not None:
        for wfp in weights_priority_order:
            if wfp in raw_rd.weights:
                raw_rd.weights = {wfp: raw_rd.weights[wfp]}
                break
        else:
            raise ValueError(f"Not found any of the specified weights formats {weights_priority_order}")

    return raw_rd
