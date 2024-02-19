import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Union

import pytest
from ruyaml import YAML

yaml = YAML(typ="safe")

EXAMPLE_SPECS = Path(__file__).parent / "../example_descriptions/"
GENERATED_JSON_SCHEMAS = Path(__file__).parent / "generated_json_schemas"
UNET2D_ROOT = EXAMPLE_SPECS / "models/unet2d_nuclei_broad"


@pytest.fixture(scope="session")
def bioimageio_json_schema() -> Dict[Any, Any]:
    from scripts.generate_json_schemas import generate_json_schemas

    generate_json_schemas(GENERATED_JSON_SCHEMAS, "generate")
    with (GENERATED_JSON_SCHEMAS / "bioimageio_schema_latest.json").open() as f:
        schema: Union[Any, Dict[Any, Any]] = json.load(f)

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
