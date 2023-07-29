from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass, field
from email.policy import default
import inspect
import shutil
from tkinter.tix import MAX
from types import ModuleType
from pathlib import Path
from typing import Annotated, Any, Dict, Iterator, Optional, Sequence, Type, List, Tuple, Union, get_args

from pydantic.alias_generators import to_pascal, to_snake
from pydantic_core import PydanticUndefined
from bioimageio.spec import ResourceDescription, application, collection, dataset, generic, model, notebook

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
    def indent_with_symbol(self):
        spaces = " " * max(0, self.indent_level - 2)
        if len(self.loc) == 1:
            symbol = "## "
        else:
            symbol = "* "

        return f"{spaces}{symbol}"

    @property
    def indent_level(self):
        return max(0, len(self.loc) - 1) * 2

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
        return unindent(self.info.description or "")

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
            d = self.info.get_default(call_default_factory=True)
            if d == "":
                d = r"\<empty string\>"

            return f" = {d}"

    @property
    def md(self) -> str:
        nested = ""
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
                nested += "\n" + self.indent_spaces + sub_anno + ":" + subfields

        if nested and self.indent_level == 0:
            ret = (
                f"{self.indent_with_symbol}{self.name}{self.default}\n<details><summary>{self.type_annotation}\n\n"
                f"{self.explanation}\n\n</summary>\n{nested}\n</details>\n"
            )
        else:
            ret = f"{self.indent_with_symbol}{self.name}{self.default}\n{self.type_annotation}\n{self.explanation}{nested}\n"

        return ret


def get_documentation_file_name(rd_class: Type[ResourceDescription], *, latest: bool = False):
    typ = to_snake(rd_class.__name__)
    if latest:
        v = "latest"
    else:
        v = f"v{rd_class.implemented_format_version.replace('.', '-')}"

    return f"{typ}_{v}.md"


def unindent(text: str, ignore_first_line: bool = True):
    """remove minimum count of spaces at beginning of each line.

    Args:
        text: indented text
        ignore_first_line: allows to correctly unindent doc strings
    """
    first = int(ignore_first_line)
    lines = text.split("\n")
    filled_lines = [line for line in lines[first:] if line]
    if len(filled_lines) < 2:
        return "\n".join(line.strip() for line in lines)

    indent = min(len(line) - len(line.lstrip(" ")) for line in filled_lines)
    return "\n".join(lines[:first] + [line[indent:] for line in lines[first:]])


def export_documentation(folder: Path, rd_class: Type[ResourceDescription]) -> Path:
    type_footnotes: OrderedDict[str, str] = OrderedDict()
    md = "# " + (rd_class.model_config.get("title") or "") + "\n" + (unindent(rd_class.__doc__ or ""))
    field_names = ["type", "format_version"] + [
        fn for fn in rd_class.model_fields if fn not in ("type", "format_version")
    ]
    for field_name in field_names:
        info = rd_class.model_fields[field_name]
        md += "\n" + Field((field_name,), info, type_footnotes=type_footnotes, rd_class=rd_class).md

    md += "\n"
    for i, full in enumerate(type_footnotes, start=1):
        md += f"\n[^{i}]: {full}"

    file_path = folder / get_documentation_file_name(rd_class)
    file_path.write_text(md, encoding="utf-8")
    print(f"written {file_path}")
    return file_path


def export_module_documentations(folder: Path, module: ModuleType):
    rd_name = to_pascal(module.__name__.split(".")[-1])

    rd_class = None
    latest = None
    v = None
    for v in sorted(dir(module)):
        v_module = getattr(module, v)
        if not hasattr(v_module, rd_name):
            continue

        rd_class = getattr(v_module, rd_name)
        latest = export_documentation(folder, rd_class)

    assert latest is not None
    assert rd_class is not None
    shutil.copy(str(latest), folder / get_documentation_file_name(rd_class, latest=True))
    print(f" copied {latest} as latest")


if __name__ == "__main__":
    dist = (Path(__file__).parent / "../dist").resolve()
    dist.mkdir(exist_ok=True)

    export_module_documentations(dist, application)
    export_module_documentations(dist, collection)
    export_module_documentations(dist, dataset)
    export_module_documentations(dist, generic)
    export_module_documentations(dist, model)
    export_module_documentations(dist, notebook)
