import json
from pathlib import Path

from marshmallow_jsonschema.extensions import ReactJsonSchemaFormJSONSchema

import bioimageio.spec

try:
    from typing import Any, Dict, List, get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore


class BioimageioJSONSchema(ReactJsonSchemaFormJSONSchema):
    def _from_union_schema(self, obj, field) -> Dict[str, List[Any]]:
        """remove duplicate options"""
        json_schema = super()._from_union_schema(obj, field)
        wo_duplicates = []
        for option in json_schema["anyOf"]:
            if option not in wo_duplicates:
                wo_duplicates.append(option)

        if len(wo_duplicates) == 1:
            return wo_duplicates[0]
        else:
            json_schema["anyOf"] = wo_duplicates
            return json_schema


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

    json_schema, ui_schema = BioimageioJSONSchema().dump_with_uischema(getattr(spec.schema, type_)())
    with path.open("w") as f:
        json.dump(json_schema, f, indent=4, sort_keys=True)

    with path.with_name(f"{path.stem}_ui.json").open("w") as f:
        json.dump(ui_schema, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    dist = Path(__file__).parent / "../dist"
    dist.mkdir(exist_ok=True)

    import bioimageio.spec.rdf.v0_2
    import bioimageio.spec.collection.v0_2
    import bioimageio.spec.dataset.v0_2
    import bioimageio.spec.model.v0_3
    import bioimageio.spec.model.v0_4

    export_json_schema_from_schema(dist, bioimageio.spec.rdf)
    # export_json_schema_from_schema(dist, bioimageio.spec.rdf.v0_2)
    # export_json_schema_from_schema(dist, bioimageio.spec.collection)
    # export_json_schema_from_schema(dist, bioimageio.spec.collection.v0_2)
    # export_json_schema_from_schema(dist, bioimageio.spec.dataset.v0_2)
    export_json_schema_from_schema(dist, bioimageio.spec.model)
    # export_json_schema_from_schema(dist, bioimageio.spec.model.v0_3)
    # export_json_schema_from_schema(dist, bioimageio.spec.model.v0_4)
