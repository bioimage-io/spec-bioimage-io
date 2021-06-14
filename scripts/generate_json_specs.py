import json
from pathlib import Path

from marshmallow_jsonschema import JSONSchema

import bioimageio.spec
from bioimageio.spec.schema import Model


def export_json_model_spec(path: Path):
    model_schema = Model()

    with path.open("w") as f:
        json_schema = JSONSchema().dump(model_schema)
        json.dump(json_schema, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    export_json_model_spec(Path(__file__).parent / f"../dist/model_spec_{bioimageio.spec.__version__}.json")
