import dataclasses
import inspect
import typing
from pathlib import Path

import bioimageio.spec


@dataclasses.dataclass
class DocNode:
    type_name: str
    description: str
    sub_docs: typing.List[typing.Tuple[typing.Union["DocNode", str], "DocNode"]]
    details: typing.List["DocNode"]
    many: bool  # expecting a list of the described sub spec
    optional: bool
    maybe_optional: bool

    def __post_init__(self):
        assert not (self.sub_docs and self.details)


def doc_from_schema(obj, spec=bioimageio.spec) -> DocNode:
    if obj is None:
        return DocNode(
            type_name="Any", description="", sub_docs=[], details=[], many=False, optional=False, maybe_optional=False
        )
    elif isinstance(obj, spec.fields.Nested):
        type_name = obj.type_name
        many = obj.many
        description = obj.bioimageio_description
        maybe_required = obj.bioimageio_maybe_required
        obj = obj.nested
    else:
        type_name = ""
        description = ""
        many = False
        maybe_required = False

    description += obj.bioimageio_description
    details = []
    sub_docs = []
    required = True
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
        sub_docs = [(name, doc_from_schema(nested_field)) for name, nested_field in sub_fields]
    else:
        type_name += obj.type_name
        required = obj.required
        maybe_required = obj.bioimageio_maybe_required
        if isinstance(obj, spec.fields.Union):
            details = [doc_from_schema(opt) for opt in obj._candidate_fields]
        elif isinstance(obj, spec.fields.Dict):
            details = [
                dict_descr
                for dict_descr in [doc_from_schema(obj.key_field), doc_from_schema(obj.value_field)]
                if dict_descr.description
            ]
        elif isinstance(obj, spec.fields.List):
            inner_doc = doc_from_schema(obj.inner)
            if inner_doc.description or inner_doc.sub_docs or inner_doc.details:
                details = [inner_doc]
        else:
            assert isinstance(obj, spec.fields.DocumentedField), (type(obj), obj)

    return DocNode(
        type_name=type_name,
        description=description,
        sub_docs=sub_docs,
        details=details,
        many=many,
        optional=not required,
        maybe_optional=maybe_required,
    )


def markdown_from_doc(doc: DocNode, indent: int = 0):
    if doc.sub_docs:
        sub_docs = [(name, sdn) for name, sdn in doc.sub_docs]
        enumerate_symbol: typing.Optional[str] = "*"
    elif doc.details:
        sub_docs = [("", sdn) for sdn in doc.details]
        enumerate_symbol = "1."
    else:
        sub_docs = []
        enumerate_symbol = None

    sub_doc = ""
    for name, sdn in sub_docs:
        if isinstance(name, DocNode):
            name = markdown_from_doc(name, indent=indent).strip().strip("_")

            print("name", name)

        name = f"`{name}` " if name else ""
        sub_doc += f"{'  ' * indent}{enumerate_symbol} {name}{markdown_from_doc(sdn, indent+1)}"

    type_name = (
        f"{'optional' if doc.optional else ''}{'*' if doc.maybe_optional else ''}{' ' if doc.optional else ''}"
        f"{doc.type_name}"
    )
    if type_name:
        type_name = f"_{type_name}_ "

    return f"{type_name}{doc.description}\n{sub_doc}"


def export_markdown_doc_from_schema(path: Path, schema: bioimageio.spec.schema.SharedBioImageIOSchema) -> None:
    doc = doc_from_schema(schema)
    md_doc = markdown_from_doc(doc)
    path.write_text(md_doc, encoding="utf-8")


def export_markdown_docs(folder: Path, spec=bioimageio.spec):
    if spec == bioimageio.spec:
        format_version_wo_patch = "latest"
    else:
        format_version_wo_patch = spec.__name__.split(".")[-1]

    export_markdown_doc_from_schema(folder / f"model_spec_{format_version_wo_patch}.md", spec.schema.Model())
    export_markdown_doc_from_schema(folder / f"rdf_spec_{format_version_wo_patch}.md", spec.schema.RDF())


if __name__ == "__main__":
    dist = Path(__file__).parent / "../dist"
    dist.mkdir(exist_ok=True)

    export_markdown_docs(dist)
    export_markdown_docs(dist, bioimageio.spec.v0_3)
