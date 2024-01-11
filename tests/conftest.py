from pathlib import Path
from types import MappingProxyType

import pytest
from ruamel.yaml import YAML

yaml = YAML(typ="safe")

EXAMPLE_SPECS = Path(__file__).parent / "../example_descriptions/"

UNET2D_ROOT = EXAMPLE_SPECS / "models/unet2d_nuclei_broad"


@pytest.fixture(scope="session")
def stardist04_data():
    with (EXAMPLE_SPECS / "models/stardist_example_model/v0_4.bioimageio.yaml").open() as f:
        return MappingProxyType(yaml.load(f))


@pytest.fixture(scope="session")
def unet2d_data():
    with (UNET2D_ROOT / "bioimageio.yaml").open() as f:
        data = yaml.load(f)

    return MappingProxyType(data)
