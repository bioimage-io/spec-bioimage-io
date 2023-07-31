import json
from pathlib import Path
from typing import Any, Dict

from pydantic import ConfigDict, TypeAdapter

import bioimageio.spec


def export_json_schemas_from_type(folder: Path, type_: Any, *, name: str, title: str):
    adapter = TypeAdapter(
        type_,
        config=ConfigDict(title=title),
    )
    schema = adapter.json_schema()
    for version in ("_".join(bioimageio.spec.__version__.split(".")), "latest"):
        write_schema(schema, folder / f"{name}_{version}.json")


def write_schema(schema: Dict[str, Any], path: Path):
    with path.open("w") as f:
        json.dump(schema, f, indent=4)

    print(f"written `{path}")


if __name__ == "__main__":
    dist = (Path(__file__).parent / "../dist").resolve()
    dist.mkdir(exist_ok=True)

    export_json_schemas_from_type(
        dist,
        bioimageio.spec.ResourceDescription,
        name="bioimageio_spec",
        title=f"bioimage.io resource description {bioimageio.spec.__version__}",
    )
