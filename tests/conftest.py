from pathlib import Path
from urllib.request import urlretrieve

import pytest

from bioimageio.spec.shared import yaml


@pytest.fixture
def _unet2d_nuclei_broad_base_url():
    return (
        "https://raw.githubusercontent.com/bioimage-io/"
        "spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/"
    )


@pytest.fixture
def unet2d_nuclei_broad_path(tmp_path):
    p = tmp_path / "unet2d_nuclei_broad"
    p.mkdir()
    yield p


def get_unet2d_nuclei_broad(_unet2d_nuclei_broad_base_url, unet2d_nuclei_broad_path, request) -> dict:
    if request.param == "v0_3_2":
        v = ""
    else:
        v = f"_{request.param}"

    f_name = f"rdf{v}.yaml"
    url = _unet2d_nuclei_broad_base_url + f_name
    path = unet2d_nuclei_broad_path / f_name
    urlretrieve(url, str(path))
    return yaml.load(path)


@pytest.fixture(params=["v0_1_0", "v0_3_0", "v0_3_1", "v0_3_2"])
def unet2d_nuclei_broad_any(_unet2d_nuclei_broad_base_url, unet2d_nuclei_broad_path, request) -> dict:
    yield get_unet2d_nuclei_broad(_unet2d_nuclei_broad_base_url, unet2d_nuclei_broad_path, request)


@pytest.fixture(params=["v0_3_2"])
def unet2d_nuclei_broad_latest(_unet2d_nuclei_broad_base_url, unet2d_nuclei_broad_path, request) -> dict:
    yield get_unet2d_nuclei_broad(_unet2d_nuclei_broad_base_url, unet2d_nuclei_broad_path, request)


@pytest.fixture(params=["v0_1_0", "v0_3_2"])
def unet2d_nuclei_broad_any_minor(_unet2d_nuclei_broad_base_url, unet2d_nuclei_broad_path, request) -> dict:
    yield get_unet2d_nuclei_broad(_unet2d_nuclei_broad_base_url, unet2d_nuclei_broad_path, request)


@pytest.fixture
def FruNet_model_url():
    return "https://raw.githubusercontent.com/deepimagej/models/master/fru-net_sev_segmentation/model.yaml"
