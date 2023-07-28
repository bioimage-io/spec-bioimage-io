from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass, field
from email.policy import default
import inspect
from tkinter.tix import MAX
from types import ModuleType
from pathlib import Path
from typing import Annotated, Any, Dict, Iterator, Optional, Sequence, Type, List, Tuple, Union, get_args

from pydantic.alias_generators import to_pascal, to_snake
from pydantic_core import PydanticUndefined
from bioimageio.spec import ResourceDescription, collection

from bioimageio.spec.shared.nodes import FrozenDictNode, Node
from pydantic.fields import FieldInfo
from pprint import pformat

Loc = Tuple[str, ...]

ANNOTATION_MAP = {
    "pydantic_core._pydantic_core.Url": "Url",
    "typing.": "",
    "bioimageio.spec.shared.nodes.FrozenDictNode": "Dict",
    "bioimageio.spec.shared.types.": "",
    "bioimageio.spec.": "",
    "NoneType": "None",
    "Ellipsis": "...",
}
MAX_LINE_WIDTH = 120


def get_subnodes(loc: Loc, annotation: Any) -> Iterator[Tuple[Loc, Type[Node]]]:
    try:
        is_node = issubclass(annotation, Node)
    except TypeError:
        is_node = False

    if is_node:
        yield loc, annotation
    else:
        for like_list in ["List", "Tuple", "Set"]:
            if str(annotation).startswith(f"typing.{like_list}["):
                loc = loc[:-1] + (loc[-1] + ".i",)
                break

        for sa in get_args(annotation):
            yield from get_subnodes(loc, sa)


@dataclass
class AnnotationName:
    annotation: Any
    indent_level: int
    type_footnotes: OrderedDict[str, str]
    annotation_name: str = field(init=False)
    annotation_map: Dict[str, str]

    def __post_init__(self):
        self.annotation_name = self.get_annotation_name(self.annotation)

    def slim(self, s: str):
        """shortening that's always OK"""
        s = s.strip("'\"")
        if s.startswith("<class ") and s.endswith(">"):
            s = s[len("<class ") : -1]

        s = s.strip("'\"")
        for k, v in self.annotation_map.items():
            if s.startswith(k):
                s = v + s[len(k) :]
                break

        return s.strip("'\"")

    def get_inline_name(self, t: Any, abbreviate: bool) -> str:
        s = self.slim(str(t))
        if s.startswith("Annotated["):
            args = get_args(t)
            if abbreviate:
                return f"{self.get_inline_name(args[0], abbreviate)}*"
            else:
                return (
                    f"{self.get_inline_name(args[0], abbreviate)} "
                    f"({'; '.join([self.get_inline_name(tt, abbreviate) for tt in args[1:]])})"
                )

        # if s.startswith("Union["):
        #     return "  |  ".join([self.get_inline_name(tt, abbreviate) for tt in get_args(t)])

        for format_like_list in ["List", "Tuple", "Dict", "Set", "Literal", "Union"]:
            if not s.startswith(format_like_list):
                continue

            args = get_args(t)
            if len(args) > 4 and abbreviate:
                args = [args[0], "...", args[-1]]

            parts = [self.get_inline_name(tt, abbreviate) for tt in args]
            return f"{format_like_list}[{', '.join(parts)}]"

        if s.startswith("Optional["):
            return f"Optional[{self.get_inline_name(get_args(t)[0], abbreviate=abbreviate)}]"

        return s

    def get_annotation_name(self, t: Any) -> str:
        full_inline = self.get_inline_name(t, abbreviate=False)
        if self.indent_level + len(full_inline) > MAX_LINE_WIDTH:
            abbreviated = self.type_footnotes.setdefault(full_inline, self.get_inline_name(t, abbreviate=True))
            return abbreviated + f"[^{list(self.type_footnotes).index(full_inline) + 1}]"
        else:
            return full_inline


class Field:
    def __init__(
        self, loc: Loc, info: FieldInfo, *, type_footnotes: OrderedDict[str, str], rd_class: type[ResourceDescription]
    ) -> None:
        assert loc
        self.loc = loc
        self.info = info
        self.type_footnotes = type_footnotes
        self.annotation_map = {f"{rd_class.__module__}.": "", **ANNOTATION_MAP}
        self.rd_class = rd_class

    @property
    def indent_symbol(self):
        if len(self.loc) == 1:
            return "##"
        else:
            return "*"

    @property
    def indent_level(self):
        if len(self.loc) < 3:
            return 0
        else:
            return (len(self.loc) - 2) * 2

    @property
    def indent_spaces(self):
        return " " * self.indent_level

    @property
    def name(self):
        if len(self.loc) == 1:
            return f"`{self.loc[0]}`"
        else:
            name = ".".join(map(str, self.loc))
            return f'<a id="{name}"></a>`{name}`'

    @property
    def type_annotation(self):
        return AnnotationName(
            annotation=self.info.annotation,
            type_footnotes=self.type_footnotes,
            indent_level=self.indent_level,
            annotation_map=self.annotation_map,
        ).annotation_name

    @property
    def title(self):
        return self.info.title or ""

    @property
    def description(self):
        return "\n".join([d.strip() for d in (self.info.description or "").split("\n")])

    @property
    def explanation(self):
        ret = self.indent_spaces
        if self.info.title:
            ret += f"{self.title}: "
            if "\n" in self.description or len(ret) + len(self.description) > MAX_LINE_WIDTH:
                ret += "\n"

        ret += self.description

        return ret.replace("\n", self.indent_spaces + "\n")

    @property
    def default(self):
        if self.info.default is PydanticUndefined:
            return ""
        else:
            return f" = {self.info.get_default(call_default_factory=True)}"

    @property
    def md(self) -> str:
        # anno = self.type_annotation
        # default = self.default
        # if default:
        #     anno_default_separator = "\n" + self.indent_spaces
        # #     if self.indent_level + len(anno) + 2 + len(default) <= MAX_LINE_WIDTH:
        # #         anno_default_separator = ", "
        # #     else:
        # else:
        #     anno_default_separator = ""

        # anno_default = f"{self.indent_spaces}{anno}{anno_default_separator}{default}"

        ret = f"{self.indent_spaces}{self.indent_symbol} " + "\n".join(
            [self.name + self.default, self.type_annotation, self.explanation]
        )

        for subloc, subnode in get_subnodes(self.loc, self.info.annotation):
            sub_anno = AnnotationName(
                annotation=subnode,
                type_footnotes=self.type_footnotes,
                indent_level=self.indent_level + 2,
                annotation_map=self.annotation_map,
            ).annotation_name
            subfields = ""
            for sfn, sinfo in subnode.model_fields.items():
                subfields += (
                    "\n" + Field(subloc + (sfn,), sinfo, type_footnotes=self.type_footnotes, rd_class=self.rd_class).md
                )
            if subfields:
                ret += "\n" + self.indent_spaces + sub_anno + ":" + subfields

        return ret


def export_markdown_docs(folder: Path, rd_class: Type[ResourceDescription]):
    type_footnotes: OrderedDict[str, str] = OrderedDict()
    md = "# " + (rd_class.model_config.get("title") or "") + "\n" + (rd_class.__doc__ or "")
    field_names = ["type", "format_version"] + [
        fn for fn in rd_class.model_fields if fn not in ("type", "format_version")
    ]
    for field_name in field_names:
        info = rd_class.model_fields[field_name]
        md += "\n" + Field((field_name,), info, type_footnotes=type_footnotes, rd_class=rd_class).md

    md += "\n"
    for i, full in enumerate(type_footnotes, start=1):
        md += f"\n[^{i}]: {full}"

    file_path = (
        folder / f"{rd_class.model_fields['type'].default}_v{rd_class.implemented_format_version.replace('.', '-')}.md"
    )
    file_path.write_text(md, encoding="utf-8")
    print(f"written {file_path}")


if __name__ == "__main__":
    dist = Path(__file__).parent / "../dist"
    dist.mkdir(exist_ok=True)

    export_markdown_docs(dist, collection.v0_2.Collection)

# @dataclass
# class DocLeaf:
#     type: str
#     description: str


# @dataclass
# class DocNode:
#     type: str
#     description: str

# from __future__ import annotations
# from dataclasses import dataclass
# import inspect
# from types import ModuleType
# from pathlib import Path
# from typing import Optional, Sequence, Type, List, Tuple

# import bioimageio.spec

# from pydantic.alias_generators import to_pascal, to_snake

# from bioimageio.spec.shared.nodes import FrozenDictNode, Node


# @dataclass
# class DocNode:
#     type_name: str
#     short_description: str
#     description: str
#     sub_docs: List[Tuple[str, DocNode]]
#     details: List[DocNode]
#     many: bool  # expecting a list of the described sub spec
#     optional: bool
#     maybe_optional: bool

#     def __post_init__(self):
#         assert not (self.sub_docs and self.details)

# def doc_from_node(node: Type[Node]) -> DocNode:
#     if issubclass(node, FrozenDictNode):
#         return DocNode(node.__name__, short_description=node.model_config.get("title", ""), description=node.__doc__, sub_docs=[() for n])

#     for name, field in node:

#     if obj is None:
#         return DocNode(
#             type_name="Any",
#             short_description="",
#             description="",
#             sub_docs=[],
#             details=[],
#             many=False,
#             optional=False,
#             maybe_optional=False,
#         )
#     elif isinstance(obj, fields.Nested):
#         type_name = obj.type_name
#         many = obj.many
#         short_description = obj.short_bioimageio_description
#         description = obj.bioimageio_description
#         maybe_required = obj.bioimageio_maybe_required
#         required = obj.required
#         obj = obj.nested
#     else:
#         type_name = ""
#         short_description = obj.short_bioimageio_description
#         description = obj.bioimageio_description
#         many = False
#         maybe_required = False
#         required = True

#     if callable(description):
#         description = description()

#     if callable(short_description):
#         short_description = short_description()

#     details = []
#     sub_docs = []
#     if inspect.isclass(obj) and issubclass(obj, spec.schema.SharedBioImageIOSchema):
#         obj = obj()

#     if isinstance(obj, spec.schema.SharedBioImageIOSchema):

#         def sort_key(name_and_nested_field):
#             name, nested_field = name_and_nested_field
#             if nested_field.bioimageio_description_order is None:
#                 manual_order = ""
#             else:
#                 manual_order = f"{nested_field.bioimageio_description_order:09}"

#             return f"{manual_order}{int(not nested_field.required)}{name}"

#         sub_fields = sorted(obj.fields.items(), key=sort_key)
#         sub_docs = [(name, doc_from_node(nested_field, spec)) for name, nested_field in sub_fields]
#     else:
#         type_name += obj.type_name
#         required = obj.required
#         maybe_required = obj.bioimageio_maybe_required
#         if isinstance(obj, fields.Union):
#             details = [doc_from_node(opt, spec) for opt in obj._candidate_fields]
#         elif isinstance(obj, fields.Dict):
#             details = [doc_from_node(obj.key_field, spec), doc_from_node(obj.value_field, spec)]
#         elif isinstance(obj, fields.list):
#             details = [doc_from_node(obj.inner, spec)]
#         else:
#             assert isinstance(obj, fields.DocumentedField), (type(obj), obj)

#     return DocNode(
#         type_name=type_name,
#         short_description=short_description,
#         description=description,
#         sub_docs=[(name, d) for name, d in sub_docs if d.description or d.sub_docs or d.details],
#         details=[d for d in details if d.description or d.sub_docs or d.details],
#         many=many,
#         optional=not required,
#         maybe_optional=maybe_required,
#     )


# def markdown_from_doc(
#     doc: DocNode, parent_names: Sequence[str] = tuple(), neither_opt_nor_req: bool = False, indent_lvl: int = 0
# ) -> str:
#     if doc.sub_docs:
#         sub_docs = [(name, sdn) for name, sdn in doc.sub_docs]
#         enumerate_symbol: Optional[str] = "*"
#     elif doc.details:
#         sub_docs = [("", sdn) for sdn in doc.details]
#         enumerate_symbol = "1."
#     else:
#         sub_docs = []
#         enumerate_symbol = None

#     n_o_n_r = neither_opt_nor_req or doc.type_name.startswith("list") or doc.type_name.startswith("Dict")
#     sub_doc = ""
#     if not doc.short_description:
#         for name, sdn in sub_docs:
#             field_path = [n for n in [*parent_names, name] if n]
#             assert isinstance(name, str), name  # earlier version allowed DocNode here
#             name = f'<a id="{":".join(field_path)}"></a>`{name}`' if name else ""
#             entry = markdown_from_doc(sdn, field_path, neither_opt_nor_req=n_o_n_r, indent_lvl=indent_lvl + 1)
#             if entry:
#                 sub_doc += f"{enumerate_symbol} {name} {entry}"

#     if doc.type_name:
#         opt = (
#             ""
#             if neither_opt_nor_req
#             else "optional* "
#             if doc.maybe_optional
#             else "optional "
#             if doc.optional
#             else "required "
#         )
#         type_name = f"_({opt}{doc.type_name})_ "
#     else:
#         type_name = ""

#     md_doc = f"{type_name}{doc.short_description or doc.description}\n{sub_doc}"
#     indent = "    "
#     if indent_lvl:
#         md_doc = f"\n{indent}".join(md_doc.strip().split("\n"))

#     return md_doc + "\n"


# def export_markdown_doc(folder: Path, node: Type[Node], as_latest: bool = False) -> None:
#     module = node.__module__.replace("bioimageio.spec.", "")
#     assert "." in module
#     module, version = module.split(".")
#     assert version.startswith("v")
#     if as_latest:
#         version = "latest"
#     else:
#         version = version[1:]

#     name = to_snake(node.__name__)
#     path = folder / f"{name}_spec_{version}.md"

#     doc = doc_from_node(node)
#     md_doc = markdown_from_doc(doc)
#     path.write_text(md_doc, encoding="utf-8")
#     print(f"written {path}")


# def export_markdown_docs(folder: Path, module: ModuleType):
#     node_name = to_pascal(module.__name__.split(".")[-1])
#     node_name = node_name.replace("Generic", "GenericDescription")

#     for v in dir(module):
#         if not v.startswith("v") or "_" not in v:
#             continue

#         v_module = getattr(module, v)
#         v_node = getattr(v_module, node_name)
#         export_markdown_doc(folder, v_node)

#     latest_node = getattr(module, node_name)
#     assert issubclass(latest_node, Node)
#     export_markdown_doc(folder, latest_node, as_latest=True)


# if __name__ == "__main__":
#     dist = Path(__file__).parent / "../dist"
#     dist.mkdir(exist_ok=True)

#     export_markdown_docs(dist, bioimageio.spec.collection.v0_2.Collection)
#     # export_markdown_docs(dist, bioimageio.spec.dataset)
#     # export_markdown_docs(dist, bioimageio.spec.generic)
#     # export_markdown_docs(dist, bioimageio.spec.model)
