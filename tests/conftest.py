from pathlib import Path
from pprint import pprint
from types import MappingProxyType
from typing import Any, Dict

import pytest
from dotenv import load_dotenv

from bioimageio.spec._internal.constants import (
    KNOWN_GITHUB_USERS,
    KNOWN_INVALID_GITHUB_USERS,
    N_KNOWN_GITHUB_USERS,
    N_KNOWN_INVALID_GITHUB_USERS,
)
from bioimageio.spec._internal.io_utils import read_yaml
from bioimageio.spec._internal.type_guards import is_kwargs
from bioimageio.spec.utils import get_bioimageio_json_schema

_ = load_dotenv()

EXAMPLE_DESCRIPTIONS = Path(__file__).parent / "../example_descriptions/"
UNET2D_ROOT = EXAMPLE_DESCRIPTIONS / "models/unet2d_nuclei_broad"


@pytest.fixture(scope="session")
def bioimageio_json_schema() -> Dict[str, Any]:
    return get_bioimageio_json_schema()


@pytest.fixture(scope="session")
def stardist04_data():
    data = read_yaml(
        EXAMPLE_DESCRIPTIONS / "models/stardist_example_model/v0_4.bioimageio.yaml"
    )
    assert isinstance(data, dict)
    return MappingProxyType(data)


@pytest.fixture(scope="session")
def covid_if_dataset_path() -> Path:
    return EXAMPLE_DESCRIPTIONS / "datasets/covid_if_training_data/bioimageio.yaml"


@pytest.fixture(scope="session")
def unet2d_path() -> Path:
    return UNET2D_ROOT / "bioimageio.yaml"


@pytest.fixture(scope="session")
def unet2d_path_old() -> Path:
    return UNET2D_ROOT / "v0_4_9.bioimageio.yaml"


@pytest.fixture(scope="session")
def unet2d_data(unet2d_path: Path):
    data = read_yaml(unet2d_path)
    assert is_kwargs(data)
    return MappingProxyType(data)


def pytest_sessionfinish(session: Any, exitstatus: Any):
    if len(KNOWN_GITHUB_USERS) > N_KNOWN_GITHUB_USERS:
        print("updated known gh users:")
        pprint(KNOWN_GITHUB_USERS)

    if len(KNOWN_INVALID_GITHUB_USERS) > N_KNOWN_INVALID_GITHUB_USERS:
        print("updated known invalid gh users:")
        pprint(KNOWN_INVALID_GITHUB_USERS)
