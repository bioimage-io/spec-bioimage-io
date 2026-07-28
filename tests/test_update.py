from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Literal

import pytest


@pytest.mark.parametrize(
    "output,preload", [(None, False), (StringIO(), False), ("path", True)]
)
def test_update_format(
    unet2d_path: str,
    output: None | StringIO | Literal["path"],
    preload: bool,
    tmp_path: Path,
):
    from bioimageio.spec import load_description
    from bioimageio.spec._update import update_format
    from bioimageio.spec.model import ModelDescr

    if preload:
        src = load_description(unet2d_path, perform_io_checks=False)
    else:
        src = unet2d_path

    updated = update_format(
        src,
        perform_io_checks=False,
        output=tmp_path if output == "path" else output,
    )
    assert updated.type == "model"
    assert updated.format_version == ModelDescr.implemented_format_version


@pytest.mark.parametrize("preload", [False, True])
def test_update_hashes(unet2d_path: str, preload: bool):
    from bioimageio.spec import InvalidDescr, load_model_description
    from bioimageio.spec._update import update_hashes

    if preload:
        src = load_model_description(unet2d_path, perform_io_checks=False)
    else:
        src = unet2d_path

    updated = update_hashes(src)
    assert not isinstance(updated, InvalidDescr)
