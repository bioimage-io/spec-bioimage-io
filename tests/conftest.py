from pathlib import Path
from types import MappingProxyType

import pytest
from ruamel.yaml import YAML

yaml = YAML(typ="safe")

EXAMPLE_SPECS = Path(__file__).parent / "../example_specs"


@pytest.fixture(scope="session")
def stardist04_data():
    with (EXAMPLE_SPECS / "models/stardist_example_model/rdf_v0_4.yaml").open() as f:
        return MappingProxyType(yaml.load(f))


@pytest.fixture(scope="session")
def unet2d_root() -> Path:
    return EXAMPLE_SPECS / "models/unet2d_nuclei_broad"


@pytest.fixture(scope="session")
def unet2d_data(unet2d_root: Path):
    with (unet2d_root / "rdf.yaml").open() as f:
        data = yaml.load(f)

    return MappingProxyType(data)
