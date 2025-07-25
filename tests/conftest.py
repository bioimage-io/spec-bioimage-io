import json
from pathlib import Path
from pprint import pprint
from types import MappingProxyType
from typing import Any, Dict, Union

import pytest
from dotenv import load_dotenv

from bioimageio.spec._internal.constants import (
    KNOWN_GITHUB_USERS,
    KNOWN_INVALID_GITHUB_USERS,
    N_KNOWN_GITHUB_USERS,
    N_KNOWN_INVALID_GITHUB_USERS,
)
from bioimageio.spec._internal.io_utils import read_yaml
from bioimageio.spec._internal.type_guards import is_dict, is_kwargs

try:
    from filelock import FileLock
except ImportError:
    FileLock = None

_ = load_dotenv()

EXAMPLE_DESCRIPTIONS = Path(__file__).parent / "../example_descriptions/"
UNET2D_ROOT = EXAMPLE_DESCRIPTIONS / "models/unet2d_nuclei_broad"


@pytest.fixture(scope="session")
def bioimageio_json_schema(
    tmp_path_factory: pytest.TempPathFactory, worker_id: str = "master"
) -> Dict[Any, Any]:
    """generates json schema (only run with one worker)
    see https://pytest-xdist.readthedocs.io/en/latest/how-to.html#making-session-scoped-fixtures-execute-only-once
    """
    from scripts.generate_json_schemas import generate_json_schemas

    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    path = root_tmp_dir / "bioimageio_schema_latest.json"
    if worker_id == "master":
        # no workers
        generate_json_schemas(root_tmp_dir, "generate")
        schema: Union[Any, Dict[Any, Any]] = json.loads(path.read_text())
    else:
        assert FileLock is not None
        with FileLock(path.with_suffix(path.suffix + ".lock")):
            if not path.is_file():
                generate_json_schemas(root_tmp_dir, "generate")

            schema: Union[Any, Dict[Any, Any]] = json.loads(path.read_text())

    assert is_dict(schema)
    return schema


@pytest.fixture(scope="session")
def stardist04_data():
    data = read_yaml(
        EXAMPLE_DESCRIPTIONS / "models/stardist_example_model/v0_4.bioimageio.yaml"
    )
    assert isinstance(data, dict)
    return MappingProxyType(data)


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
