from pathlib import Path
from typing import Any, Mapping

from bioimageio.spec._internal.validation_context import ValidationContext


def test_get_conda_env(unet2d_data: Mapping[str, Any], unet2d_path: Path):
    from bioimageio.spec.get_conda_env import get_conda_env
    from bioimageio.spec.model.v0_5 import PytorchStateDictWeightsDescr

    with ValidationContext(perform_io_checks=False, root=unet2d_path.parent):
        w = PytorchStateDictWeightsDescr(**unet2d_data["weights"]["pytorch_state_dict"])

    conda_env = get_conda_env(entry=w)

    assert conda_env.channels
    assert conda_env.dependencies
