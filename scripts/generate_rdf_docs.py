# todo: update
import dataclasses
import inspect
from types import ModuleType
from pathlib import Path
from typing import Type

import bioimageio.spec.rdf
from bioimageio.spec.shared import fields

from pydantic.alias_generators import to_pascal, to_snake

from bioimageio.spec.shared.nodes import FrozenDictBase, Node


def doc_from_node(node: Type[Node]) -> DocNode:


    if issubclass(node, FrozenDictBase):
        return DocNode(node.__name__, short_description=node.model_config.get("title", ""), description=node.__doc__, sub_docs=[() for n])
    for name, field in node:

    if obj is None:
        return DocNode(
            type_name="Any",
            short_description="",
            description="",
            sub_docs=[],
            details=[],
            many=False,
            optional=False,
            maybe_optional=False,
        )
    elif isinstance(obj, fields.Nested):
        type_name = obj.type_name
        many = obj.many
        short_description = obj.short_bioimageio_description
        description = obj.bioimageio_description
        maybe_required = obj.bioimageio_maybe_required
        required = obj.required
        obj = obj.nested
    else:
        type_name = ""
        short_description = obj.short_bioimageio_description
        description = obj.bioimageio_description
        many = False
        maybe_required = False
        required = True

    if callable(description):
        description = description()

    if callable(short_description):
        short_description = short_description()

    details = []
    sub_docs = []
    if inspect.isclass(obj) and issubclass(obj, spec.schema.SharedBioImageIOSchema):
        obj = obj()

    if isinstance(obj, spec.schema.SharedBioImageIOSchema):

        def sort_key(name_and_nested_field):
            name, nested_field = name_and_nested_field
            if nested_field.bioimageio_description_order is None:
                manual_order = ""
            else:
                manual_order = f"{nested_field.bioimageio_description_order:09}"

            return f"{manual_order}{int(not nested_field.required)}{name}"

        sub_fields = sorted(obj.fields.items(), key=sort_key)
        sub_docs = [(name, doc_from_node(nested_field, spec)) for name, nested_field in sub_fields]
    else:
        type_name += obj.type_name
        required = obj.required
        maybe_required = obj.bioimageio_maybe_required
        if isinstance(obj, fields.Union):
            details = [doc_from_node(opt, spec) for opt in obj._candidate_fields]
        elif isinstance(obj, fields.Dict):
            details = [doc_from_node(obj.key_field, spec), doc_from_node(obj.value_field, spec)]
        elif isinstance(obj, fields.list):
            details = [doc_from_node(obj.inner, spec)]
        else:
            assert isinstance(obj, fields.DocumentedField), (type(obj), obj)

    return DocNode(
        type_name=type_name,
        short_description=short_description,
        description=description,
        sub_docs=[(name, d) for name, d in sub_docs if d.description or d.sub_docs or d.details],
        details=[d for d in details if d.description or d.sub_docs or d.details],
        many=many,
        optional=not required,
        maybe_optional=maybe_required,
    )


def markdown_from_doc(
    doc: DocNode, parent_names: Sequence[str] = tuple(), neither_opt_nor_req: bool = False, indent_lvl: int = 0
):
    if doc.sub_docs:
        sub_docs = [(name, sdn) for name, sdn in doc.sub_docs]
        enumerate_symbol: Optional[str] = "*"
    elif doc.details:
        sub_docs = [("", sdn) for sdn in doc.details]
        enumerate_symbol = "1."
    else:
        sub_docs = []
        enumerate_symbol = None

    n_o_n_r = neither_opt_nor_req or doc.type_name.startswith("list") or doc.type_name.startswith("Dict")
    sub_doc = ""
    if not doc.short_description:
        for name, sdn in sub_docs:
            field_path = [n for n in [*parent_names, name] if n]
            assert isinstance(name, str), name  # earlier version allowed DocNode here
            name = f'<a id="{":".join(field_path)}"></a>`{name}`' if name else ""
            entry = markdown_from_doc(sdn, field_path, neither_opt_nor_req=n_o_n_r, indent_lvl=indent_lvl + 1)
            if entry:
                sub_doc += f"{enumerate_symbol} {name} {entry}"

    if doc.type_name:
        opt = (
            ""
            if neither_opt_nor_req
            else "optional* "
            if doc.maybe_optional
            else "optional "
            if doc.optional
            else "required "
        )
        type_name = f"_({opt}{doc.type_name})_ "
    else:
        type_name = ""

    md_doc = f"{type_name}{doc.short_description or doc.description}\n{sub_doc}"
    indent = "    "
    if indent_lvl:
        md_doc = f"\n{indent}".join(md_doc.strip().split("\n"))

    return md_doc + "\n"


def export_markdown_doc(folder: Path, node: Type[Node], as_latest: bool = False) -> None:
    module = node.__module__.replace("bioimageio.spec.", "")
    assert "." in module
    module, version = module.split(".")
    assert version.startswith("v")
    if as_latest:
        version = "latest"
    else:
        version = version[1:]

    name = to_snake(node.__name__)
    path = folder / f"{name}_spec_{version}.md"

    doc = doc_from_node(node)
    md_doc = markdown_from_doc(doc)
    path.write_text(md_doc, encoding="utf-8")
    print(f"written {path}")


def export_markdown_docs(folder: Path, module: ModuleType):
    node_name = to_pascal(module.__name__.split(".")[-1])
    node_name = node_name.replace("Generic", "GenericDescription")

    for v in dir(module):
        if not v.startswith("v") or "_" not in v:
            continue

        v_module = getattr(module, v)
        v_node = getattr(v_module, node_name)
        export_markdown_doc(folder, v_node)

    latest_node = getattr(module, node_name)
    assert issubclass(latest_node, Node)
    export_markdown_doc(folder, latest_node, as_latest=True)


if __name__ == "__main__":
    dist = Path(__file__).parent / "../dist"
    dist.mkdir(exist_ok=True)

    export_markdown_docs(dist, bioimageio.spec.collection)
    export_markdown_docs(dist, bioimageio.spec.dataset)
    export_markdown_docs(dist, bioimageio.spec.generic)
    export_markdown_docs(dist, bioimageio.spec.model)
