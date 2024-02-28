import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Union

import pytest
from filelock import FileLock
from ruyaml import YAML

yaml = YAML(typ="safe")

EXAMPLE_SPECS = Path(__file__).parent / "../example_descriptions/"
UNET2D_ROOT = EXAMPLE_SPECS / "models/unet2d_nuclei_broad"


@pytest.fixture(scope="session")
def bioimageio_json_schema(
    tmp_path_factory: pytest.TempPathFactory, worker_id: str
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
        with FileLock(path.with_suffix(path.suffix + ".lock")):
            if not path.is_file():
                generate_json_schemas(root_tmp_dir, "generate")

            schema: Union[Any, Dict[Any, Any]] = json.loads(path.read_text())

    assert isinstance(schema, dict)
    return schema


@pytest.fixture(scope="session")
def stardist04_data():
    with (
        EXAMPLE_SPECS / "models/stardist_example_model/v0_4.bioimageio.yaml"
    ).open() as f:
        return MappingProxyType(yaml.load(f))


@pytest.fixture(scope="session")
def unet2d_path() -> Path:
    return UNET2D_ROOT / "bioimageio.yaml"


@pytest.fixture(scope="session")
def unet2d_data(unet2d_path: Path):
    with unet2d_path.open() as f:
        data: Union[Any, Dict[Any, Any]] = yaml.load(f)

    assert isinstance(data, dict)
    return MappingProxyType(data)
