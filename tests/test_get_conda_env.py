from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

import pytest

from bioimageio.spec._internal.validation_context import ValidationContext
from bioimageio.spec.model.v0_5 import (
    OnnxWeightsDescr,
    PytorchStateDictWeightsDescr,
    TorchscriptWeightsDescr,
)


@pytest.mark.parametrize(
    "descr_class,w",
    [
        (
            PytorchStateDictWeightsDescr,
            dict(
                authors=[
                    dict(
                        name="Constantin Pape;@bioimage-io",
                        affiliation="EMBL Heidelberg",
                        orcid="0000-0001-6562-7187",
                    )
                ],
                sha256="e4d3885bccbe41cbf6c1d825f3cd2b707c7021ead5593156007e407a16b27cf2",
                source="https://zenodo.org/records/3446812/files/unet2d_weights.torch",
                architecture=dict(
                    callable="UNet2d",
                    source="unet2d.py",
                    sha256="7cdd8332dc3e3735e71c328f81b63a9ac86c028f80522312484ca9a4027d4ce1",
                    kwargs=dict(input_channels=1, output_channels=1),
                ),
                dependencies=dict(
                    source="environment.yaml",
                    sha256="129d589d2ec801398719b1a6d1bf20ea36b3632f14ccb56a24700df7d719fd10",
                ),
                pytorch_version="1.5.1",
            ),
        ),
        (
            OnnxWeightsDescr,
            dict(
                sha256="f1f086d5e340f9d4d7001a1b62a2b835f9b87a2fb5452c4fe7d8cc821bdf539c",
                source="weights.onnx",
                opset_version=12,
                parent="pytorch_state_dict",
            ),
        ),
        (
            TorchscriptWeightsDescr,
            dict(
                sha256="62fa1c39923bee7d58a192277e0dd58f2da9ee810662addadd0f44a3784d9210",
                source="weights.pt",
                parent="pytorch_state_dict",
                pytorch_version="1.5.1",
            ),
        ),
    ],
)
def test_get_conda_env(
    descr_class: Union[
        PytorchStateDictWeightsDescr, OnnxWeightsDescr, TorchscriptWeightsDescr
    ],
    w: Mapping[str, Any],
    unet2d_path: Path,
):
    from bioimageio.spec.get_conda_env import get_conda_env

    with ValidationContext(perform_io_checks=False, root=unet2d_path.parent):
        w_descr = descr_class.model_validate(w)

    conda_env = get_conda_env(entry=w_descr)

    assert conda_env.channels
    assert conda_env.dependencies


def test_get_default_pytorch_env():
    from bioimageio.spec._internal.version_type import Version
    from bioimageio.spec.get_conda_env import (
        _get_default_pytorch_env,  # pyright: ignore[reportPrivateUsage]
    )

    versions: Dict[str, List[Optional[str]]] = {
        "pytorch": [
            "1.6.0",
            "1.7.0",
            "1.7.1",
            "1.8.0",
            "1.8.1",
            "1.9.0",
            "1.9.1",
            "1.10.0",
            "1.10.1",
            "1.11.0",
            "1.12.0",
            "1.12.1",
            "1.13.0",
            "1.13.1",
            "2.0.0",
            "2.0.1",
            "2.1.0",
            "2.1.1",
            "2.1.2",
            "2.2.0",
            "2.2.1",
            "2.2.2",
            "2.3.0",
            "2.3.1",
            "2.4.0",
            "2.4.1",
            "2.5.0",
        ]
    }
    envs = [
        _get_default_pytorch_env(pytorch_version=Version.model_validate(v))
        for v in versions["pytorch"]
    ]
    for p in ["torchvision", "torchaudio"]:
        versions[p] = [
            env._get_version(p) for env in envs  # pyright: ignore[reportPrivateUsage]
        ]

    def assert_lt(p: str, i: int):
        vs = versions[p]
        a, b = vs[i], vs[i + 1]
        assert a is not None, (vs[i], vs[i + 1])
        assert b is not None, (vs[i], vs[i + 1])
        av = Version(a.strip("="))
        bv = Version(b.strip("="))
        assert av < bv, (vs[i], vs[i + 1])

    for i in range(len(versions["pytorch"]) - 1):
        assert_lt("pytorch", i)
        assert_lt("torchvision", i)
        if i > 0:
            assert_lt("torchaudio", i)
