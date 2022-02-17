import json
from pathlib import Path

from marshmallow_jsonschema import JSONSchema

import bioimageio.spec

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore


def export_json_schema_from_schema(folder: Path, spec):
    type_or_version = spec.__name__.split(".")[-1]
    format_version_wo_patch = "_".join(spec.format_version.split(".")[:2])
    if type_or_version[1:] == format_version_wo_patch:
        type_ = spec.__name__.split(".")[-2]
    else:
        format_version_wo_patch = "latest"
        type_ = type_or_version

    path = folder / f"{type_}_spec_{format_version_wo_patch}.json"

    if type_ == "rdf":
        type_ = "RDF"
    else:
        type_ = type_.title()

    with path.open("w") as f:
        json_schema = JSONSchema().dump(getattr(spec.schema, type_)())
        json.dump(json_schema, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    dist = Path(__file__).parent / "../dist"
    dist.mkdir(exist_ok=True)

    import bioimageio.spec.rdf.v0_2
    import bioimageio.spec.collection.v0_2
    import bioimageio.spec.dataset.v0_2
    import bioimageio.spec.model.v0_3
    import bioimageio.spec.model.v0_4

    export_json_schema_from_schema(dist, bioimageio.spec.rdf)
    export_json_schema_from_schema(dist, bioimageio.spec.rdf.v0_2)
    export_json_schema_from_schema(dist, bioimageio.spec.collection)
    export_json_schema_from_schema(dist, bioimageio.spec.collection.v0_2)
    export_json_schema_from_schema(dist, bioimageio.spec.dataset.v0_2)
    export_json_schema_from_schema(dist, bioimageio.spec.model)
    export_json_schema_from_schema(dist, bioimageio.spec.model.v0_3)
    export_json_schema_from_schema(dist, bioimageio.spec.model.v0_4)
