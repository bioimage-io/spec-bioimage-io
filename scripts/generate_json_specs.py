import json
from pathlib import Path

from marshmallow_jsonschema import JSONSchema

import bioimageio.spec


def export_json_schema_from_schema(path: Path, schema: bioimageio.spec.schema.SharedBioImageIOSchema):
    with path.open("w") as f:
        json_schema = JSONSchema().dump(schema)
        json.dump(json_schema, f, indent=4, sort_keys=True)


def export_json_schemas(folder: Path, spec=bioimageio.spec):
    if spec == bioimageio.spec:
        format_version_wo_patch = "latest"
    else:
        format_version_wo_patch = spec.__name__.split(".")[-1]

    export_json_schema_from_schema(folder / f"model_spec_{format_version_wo_patch}.json", spec.schema.Model())
    export_json_schema_from_schema(folder / f"rdf_spec_{format_version_wo_patch}.json", spec.schema.RDF())


if __name__ == "__main__":
    dist = Path(__file__).parent / "../dist"
    dist.mkdir(exist_ok=True)

    export_json_schemas(dist)
    export_json_schemas(dist, bioimageio.spec.v0_3)
