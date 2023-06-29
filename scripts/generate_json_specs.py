import json
from pathlib import Path
from types import ModuleType

import bioimageio.spec

from typing import Type

from bioimageio.spec.shared.nodes import Node

from pydantic.alias_generators import to_snake, to_pascal


def export_json_schemas(folder: Path, module: ModuleType):
    node_name = to_pascal(module.__name__.split(".")[-1])
    node_name = node_name.replace("Generic", "GenericDescription")

    for v in dir(module):
        if not v.startswith("v") or "_" not in v:
            continue

        v_module = getattr(module, v)
        v_node = getattr(v_module, node_name)
        export_json_schema(folder, v_node)

    latest_node = getattr(module, node_name)
    assert issubclass(latest_node, Node)
    export_json_schema(folder, latest_node, as_latest=True)


def export_json_schema(folder: Path, node: Type[Node], as_latest: bool = False):
    module = node.__module__.replace("bioimageio.spec.", "")
    assert "." in module
    module, version = module.split(".")
    assert version.startswith("v")
    if as_latest:
        version = "latest"
    else:
        version = version[1:]

    name = to_snake(node.__name__)
    schema = node.model_json_schema()

    path = folder / f"{name}_spec_{version}.json"

    with path.open("w") as f:
        json.dump(schema, f, indent=4)

    print(f"written {path}")


if __name__ == "__main__":
    dist = (Path(__file__).parent / "../dist").resolve()
    dist.mkdir(exist_ok=True)

    export_json_schemas(dist, bioimageio.spec.collection)
    export_json_schemas(dist, bioimageio.spec.dataset)
    export_json_schemas(dist, bioimageio.spec.generic)
    export_json_schemas(dist, bioimageio.spec.model)
