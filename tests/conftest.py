import json
from pathlib import Path
from types import MappingProxyType

import pytest
from ruyaml import YAML

yaml = YAML(typ="safe")

EXAMPLE_SPECS = Path(__file__).parent / "../example_descriptions/"
GENERATED_JSON_SCHEMAS = Path(__file__).parent / "generated_json_schemas"
UNET2D_ROOT = EXAMPLE_SPECS / "models/unet2d_nuclei_broad"


@pytest.fixture(scope="session")
def bioimageio_json_schema():
    from scripts.generate_json_schemas import generate_json_schemas

    generate_json_schemas(GENERATED_JSON_SCHEMAS, "generate")
    with (GENERATED_JSON_SCHEMAS / "bioimageio_schema_latest.json").open() as f:
        return json.load(f)


@pytest.fixture(scope="session")
def stardist04_data():
    with (
        EXAMPLE_SPECS / "models/stardist_example_model/v0_4.bioimageio.yaml"
    ).open() as f:
        return MappingProxyType(yaml.load(f))


@pytest.fixture(scope="session")
def unet2d_data():
    with (UNET2D_ROOT / "bioimageio.yaml").open() as f:
        data = yaml.load(f)

    return MappingProxyType(data)
