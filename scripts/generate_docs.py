import dataclasses
import inspect
import typing
from pathlib import Path

from bioimageio.spec import fields, schema


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


def doc_from_schema(obj) -> typing.Union[typing.Dict[str, DocNode], DocNode]:
    if obj is None:
        return DocNode(
            type_name="Any", description="", sub_docs=[], details=[], many=False, optional=False, maybe_optional=False
        )
    elif isinstance(obj, fields.Nested):
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
    if inspect.isclass(obj) and issubclass(obj, schema.SharedPyBioSchema):

        obj = obj()

    if isinstance(obj, schema.SharedPyBioSchema):

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
        if isinstance(obj, fields.Union):
            details = [doc_from_schema(opt) for opt in obj._candidate_fields]
        elif isinstance(obj, fields.Dict):
            details = [
                dict_descr
                for dict_descr in [doc_from_schema(obj.key_field), doc_from_schema(obj.value_field)]
                if dict_descr.description
            ]
        else:
            assert isinstance(obj, fields.DocumentedField), (type(obj), obj)

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
        enumerate_symbol = "*"
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


def markdown_from_schema(schema: schema.SharedPyBioSchema) -> str:
    doc = doc_from_schema(schema)
    return markdown_from_doc(doc)


def export_markdown_docs(folder: Path):
    doc = markdown_from_schema(schema.Model())
    (folder / "bioimageio_model_spec.md").write_text(doc, encoding="utf-8")


if __name__ == "__main__":
    export_markdown_docs(Path(__file__).parent / "../generated")
