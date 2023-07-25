import json
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Type
from pydantic import ConfigDict, TypeAdapter

from pydantic.alias_generators import to_pascal, to_snake

import bioimageio.spec
from bioimageio.spec.shared.nodes import Node


# def export_json_schemas(folder: Path, module: ModuleType):
#     node_name = to_pascal(module.__name__.split(".")[-1])

#     # export type and version specific schemas
#     version = "unknown"
#     for v in dir(module):
#         if not v.startswith("v") or "_" not in v:
#             continue

#         v_module = getattr(module, v)
#         v_node = getattr(v_module, node_name)
#         export_json_schema_from_node(folder, v_node)
#         version = v[1:]

#     # export latest schema
#     latest_node = getattr(module, node_name)
#     assert latest_node is not None
#     assert issubclass(latest_node, Node)
#     export_json_schema_from_node(folder, latest_node, as_latest=True)

#     # export type specific union (across format_version) schema
#     any_node = getattr(module, "Any" + node_name)
#     if issubclass(any_node, Node):
#         schema = any_node.model_json_schema()
#     else:
#         adapter = TypeAdapter(any_node, config=ConfigDict())
#         schema = adapter.json_schema()

#     write_schema(schema, folder / f"{node_name.lower()}_up_to_{version}.json")
#     write_schema(schema, folder / f"{node_name.lower()}_up_to_latest.json")


# def export_json_schema_from_node(folder: Path, node: Type[Node], as_latest: bool = False):
#     module = node.__module__.replace("bioimageio.spec.", "")
#     assert "." in module
#     module, version = module.split(".")
#     assert version.startswith("v")
#     if as_latest:
#         version = "latest"
#     else:
#         version = version[1:]

#     name = to_snake(node.__name__)
#     schema = node.model_json_schema()

#     write_schema(schema, folder / f"{name}_spec_{version}.json")


def export_json_schemas(folder: Path):
    export_json_schemas_from_type(
        folder,
        bioimageio.spec.ResourceDescription,
        name="bioimageio_spec",
        title=f"bioimage.io resource description {bioimageio.spec.__version__}",
    )


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

    # export_json_schemas(dist, bioimageio.spec.application)
    # export_json_schemas(dist, bioimageio.spec.collection)
    # export_json_schemas(dist, bioimageio.spec.dataset)
    # export_json_schemas(dist, bioimageio.spec.generic)
    # export_json_schemas(dist, bioimageio.spec.model)
    # export_json_schemas(dist, bioimageio.spec.notebook)
    export_json_schemas(dist)
