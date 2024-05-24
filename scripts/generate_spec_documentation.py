from __future__ import annotations

import shutil
from argparse import ArgumentParser
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from types import ModuleType
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, get_args

from pydantic.alias_generators import to_pascal, to_snake
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from bioimageio.spec import (
    ResourceDescr,
    application,
    dataset,
    generic,
    model,
    notebook,
)
from bioimageio.spec._internal.common_nodes import Node
from bioimageio.spec._internal.constants import IN_PACKAGE_MESSAGE
from bioimageio.spec._internal.utils import unindent

Loc = Tuple[str, ...]

ANNOTATION_MAP = {
    "pydantic_core._pydantic_core.Url": "Url",
    "typing.": "",
    "pathlib.": "",
    "bioimageio.spec._internal.common_nodes.FrozenDictNode": "Dict",
    "bioimageio.spec._internal.common_nodes.Kwargs": "Dict",
    "bioimageio.spec.types.": "",
    "pydantic.networks.EmailStr": "Email",
    "bioimageio.spec.": "",
    "NoneType": "None",
    "Ellipsis": "...",
    "PathType(path_type='dir')": "Directory",
}
MAX_LINE_WIDTH = 120

ADDITIONAL_DESCRIPTION_ANY_RESOURCE = (
    "\n**General notes on this documentation:**\n"
    "| symbol | explanation |\n"
    "| --- | --- |\n"
    "| `field`<sub>type hint</sub> | A fields's <sub>expected type</sub> may be"
    " shortened. "
    "If so, the abbreviated or full type is displayed below the field's description and"
    " can expanded to view "
    "further (nested) details if available. |\n"
    "| Union[A, B, ...] | indicates that a field value may be of type A or B, etc.|\n"
    "| Literal[a, b, ...] | indicates that a field value must be the specific value a"
    " or b, etc.|\n"
    "| Type* := Type (restrictions) | A field Type* followed by an asterisk indicates"
    " that annotations, e.g. "
    "value restriction apply. These are listed in parentheses in the expanded type"
    " description. "
    "They are not always intuitively understandable and merely a hint at more complex"
    " validation.|\n"
    r"| \<type\>.v\<major\>_\<minor\>.\<sub spec\> | "
    "Subparts of a spec might be taken from another spec type or format version. |\n"
    "| `field` ≝ `default` | Default field values are indicated after '≝' and make a"
    " field optional. "
    "However, `type` and `format_version` alwyas need to be set for resource"
    " descriptions written as YAML files "
    "and determine which bioimage.io specification applies. They are optional only when"
    " creating a resource "
    "description in Python code using the appropriate, `type` and `format_version`"
    " specific class.|\n"
    "| `field` ≝ 🡇 | Default field value is not displayed in-line, but in the code"
    " block below. |\n"
    f"| {IN_PACKAGE_MESSAGE} | Files referenced in fields which are marked with"
    f" '{IN_PACKAGE_MESSAGE}' "
    "are included when packaging the resource to a .zip archive. "
    "The resource description YAML file (RDF) is always included well as"
    " 'rdf.yaml'. |\n"
)


def anchor_tag(heading: str):
    a = heading.strip().strip("#")
    for rm in ",;!?./<>=`'\"":
        a = a.replace(rm, "")

    return "#" + a.replace(" ", "-")


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
    footnotes: OrderedDict[str, str]
    full_maybe_multiline: str = field(init=False)
    full_inline: str = field(init=False)
    abbreviated: Optional[str] = field(init=False)
    kind: str = field(init=False)

    annotation_map: Dict[str, str]

    def __post_init__(self):
        self.full_maybe_multiline = self.get_name(
            self.annotation, abbreviate=False, inline=False
        )
        self.full_inline = self.get_name(self.annotation, abbreviate=False)
        self.kind = self._get_kind()
        if self.indent_level + len(self.full_inline) > MAX_LINE_WIDTH:
            self.abbreviated = self.get_name(self.annotation, abbreviate=True)
        else:
            self.abbreviated = None

    def _get_kind(self):
        s = self.full_inline
        brackets = 0
        max_balance = -1
        for i in range(min(len(s), 32)):
            if s[i] == "[":
                brackets += 1

            if s[i] == "]":
                brackets -= 1

            if brackets == 0:
                max_balance = i

        return s[: max_balance + 1]

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

    def more_common_sequence_name(self, type_name: str):
        bracket = type_name.find("[")
        if bracket == -1:
            first_part = type_name
        else:
            first_part = type_name[:bracket]

        common_name = {"List": "Sequence", "Tuple": "Sequence"}.get(
            first_part, first_part
        )
        if bracket == -1:
            return common_name
        else:
            return common_name + type_name[bracket:]

    def get_name(
        self, t: Any, abbreviate: bool, inline: bool = True, multiline_level: int = 0
    ) -> str:
        if isinstance(t, FieldInfo):
            parts = list(t.metadata)
            if t.discriminator:
                parts.append(f"discriminator={t.discriminator}")

            return "; ".join(map(str, parts))

        s = self.slim(str(t))
        if s.startswith("Annotated["):
            args = get_args(t)
            if abbreviate:
                return f"{self.get_name(args[0], abbreviate, inline, multiline_level)}*"

            annotated_type = self.get_name(args[0], abbreviate, inline, multiline_level)
            annos = f"({'; '.join([self.get_name(tt, abbreviate, inline, multiline_level) for tt in args[1:]])})"
            if (
                inline
                or abbreviate
                or (
                    multiline_level + len(annotated_type) + 1 + len(annos)
                    < MAX_LINE_WIDTH
                )
            ):
                anno_sep = " "
            else:
                anno_sep = "\n" + " " * multiline_level * 2

            return f"{annotated_type}{anno_sep}{annos}"

        if s.startswith("Optional["):
            return f"Optional[{self.get_name(get_args(t)[0], abbreviate, inline, multiline_level)}]"

        for format_like_seq in ["Union", "Tuple", "Literal", "Dict", "List", "Set"]:
            if not s.startswith(format_like_seq):
                continue

            args = get_args(t)
            if format_like_seq == "Tuple" and len(args) == 2 and args[1] == ...:
                args = args[:1]

            format_like_seq_name = self.more_common_sequence_name(format_like_seq)

            if len(args) > 4 and abbreviate:
                args = [args[0], "...", args[-1]]

            parts = [
                self.get_name(tt, abbreviate, inline, multiline_level) for tt in args
            ]
            one_line = f"{format_like_seq_name}[{', '.join(parts)}]"
            if (
                abbreviate
                or inline
                or (self.indent_level + len(one_line) < MAX_LINE_WIDTH)
            ):
                return one_line

            first_line_descr = f"{format_like_seq_name} of"
            if len(args) == 1:
                more_maybe_multiline = self.get_name(
                    args[0],
                    abbreviate=abbreviate,
                    inline=inline,
                    multiline_level=multiline_level,
                )
                return first_line_descr + " " + more_maybe_multiline

            parts = [
                self.get_name(
                    tt, abbreviate, inline=inline, multiline_level=multiline_level + 1
                )
                for tt in args
            ]
            multiline_parts = f"\n{' '* multiline_level * 2}- ".join(parts)
            return (
                f"{first_line_descr}\n{' '* multiline_level * 2}- {multiline_parts}\n"
            )

        return s


class Field:
    STYLE_SWITCH_DEPTH = 4

    def __init__(
        self,
        loc: Loc,
        info: FieldInfo,
        *,
        footnotes: OrderedDict[str, str],
        rd_class: type[ResourceDescr],
        all_examples: List[Tuple[str, List[Any]]],
    ) -> None:
        super().__init__()
        assert loc
        self.loc = loc
        self.info = info
        self.footnotes = footnotes
        self.annotation_map = {f"{rd_class.__module__}.": "", **ANNOTATION_MAP}
        self.rd_class = rd_class
        self.all_examples = all_examples

    @property
    def indent_with_symbol(self):
        spaces = " " * max(0, self.indent_level - 2)
        if len(self.loc) <= self.STYLE_SWITCH_DEPTH:
            symbol = f"#{'#'* len(self.loc)} "
        else:
            symbol = "* "

        return f"{spaces}{symbol}"

    @property
    def indent_level(self):
        return max(0, len(self.loc) - self.STYLE_SWITCH_DEPTH) * 2

    @property
    def indent_spaces(self):
        return " " * self.indent_level

    @property
    def name(self):
        n = ".".join(self.loc)
        if len(self.loc) <= self.STYLE_SWITCH_DEPTH:
            return f"`{n}`"
        else:
            return f'<a id="{n}"></a>`{n}`'

    def get_explanation(self):
        title = self.info.title or ""
        description = unindent(self.info.description or "", ignore_first_line=True)
        ret = self.indent_spaces
        if title:
            ret += f"{title}: "
            if "\n" in description or len(ret) + len(description) > MAX_LINE_WIDTH:
                ret += "\n"

        ret += description.strip() + "\n"

        if self.info.examples:
            ex = "Example" if len(self.info.examples) == 1 else "Examples"
            ex = f"*{ex}:*"
            if len(self.info.examples) == 1:
                e = self.info.examples[0]
                example_inline = f"'{e}'" if isinstance(e, str) else str(e)
            else:
                example_inline = str(self.info.examples)
                if self.indent_level + len(example_inline) > MAX_LINE_WIDTH:
                    for i in range(len(self.info.examples) - 1, 0, -1):
                        example_inline = str(self.info.examples[:i] + ["…"])
                        if self.indent_level + len(example_inline) <= MAX_LINE_WIDTH:
                            break

            ret += f"[{ex}]({anchor_tag(self.name)}) {example_inline}\n"
            self.all_examples.append((self.name, self.info.examples))

        return ret.replace("\n", self.indent_spaces + "\n")

    def get_default_value(self):
        d = self.info.get_default(call_default_factory=True)
        if d is PydanticUndefined:
            return ""
        # elif d == "":
        #     d = "<empty string>"
        d_inline = f"`{d}`"
        if self.indent_level + 30 + len(d_inline) > MAX_LINE_WIDTH:
            return f" ≝ 🡇\n```python\n{pformat(d, indent=self.indent_level, width=MAX_LINE_WIDTH)}\n```\n"
        else:
            return f" ≝ {d_inline}"

    def get_md(self) -> str:
        nested = ""
        for subloc, subnode in get_subnodes(self.loc, self.info.annotation):
            sub_anno = AnnotationName(
                annotation=subnode,
                footnotes=self.footnotes,
                indent_level=self.indent_level + 2,
                annotation_map=self.annotation_map,
            ).full_inline
            subfields = ""
            for sfn, sinfo in subnode.model_fields.items():
                subfields += (
                    "\n"
                    + Field(
                        subloc + (sfn,),
                        sinfo,
                        footnotes=self.footnotes,
                        rd_class=self.rd_class,
                        all_examples=self.all_examples,
                    ).get_md()
                )
            if subfields:
                nested += f"\n{self.indent_spaces}**{sub_anno}:**{subfields}"

        an = AnnotationName(
            annotation=self.info.annotation,
            footnotes=self.footnotes,
            indent_level=self.indent_level,
            annotation_map=self.annotation_map,
        )
        first_line = (
            f"{self.indent_with_symbol}{self.name}<sub>"
            f" {an.kind}</sub>{self.get_default_value()}\n"
        )
        if (nested or an.abbreviated) and len(self.loc) <= self.STYLE_SWITCH_DEPTH:
            if an.abbreviated is None:
                expaned_type_anno = ""
            else:
                expaned_type_anno = an.full_maybe_multiline + "\n"

            ret = (
                f"{first_line}{self.get_explanation()}\n"
                f"<details><summary>{an.abbreviated or an.full_inline}\n\n</summary>\n\n"
                f"{expaned_type_anno}{nested}\n</details>\n"
            )
        else:
            if an.kind == an.full_inline:
                expaned_type_anno = ""
            else:
                expaned_type_anno = "\n" + an.full_inline

            ret = f"{first_line}{self.get_explanation()}\n{expaned_type_anno}{nested}\n"

        return ret


def get_documentation_file_name(
    rd_class: Type[ResourceDescr], *, latest: bool = False, minor: bool = False
):
    assert not (latest and minor)
    typ = to_snake(rd_class.__name__)
    if latest:
        v = "latest"
    elif minor:
        v = "v" + "-".join(rd_class.implemented_format_version.split(".")[:2])
    else:
        v = f"v{rd_class.implemented_format_version.replace('.', '-')}"

    return f"{typ}_{v}.md"


def export_documentation(folder: Path, rd_class: Type[ResourceDescr]) -> Path:
    footnotes: OrderedDict[str, str] = OrderedDict()
    all_examples: List[Tuple[str, List[Any]]] = []
    md = (
        "# "
        + (rd_class.model_config.get("title") or "")
        + "\n"
        + (
            unindent(rd_class.__doc__ or "", ignore_first_line=True)
            + ADDITIONAL_DESCRIPTION_ANY_RESOURCE
        )
    )
    all_fields = [
        (fn, info)
        for fn, info in rd_class.model_fields.items()
        if fn not in ("type", "format_version")
    ]

    def field_sort_key(fn_info: Tuple[str, FieldInfo]) -> Tuple[bool, str]:
        fn, info = fn_info
        return (
            info.get_default(call_default_factory=True) is not PydanticUndefined,
            fn,
        )

    all_fields = sorted(all_fields, key=field_sort_key)

    field_names = ["type", "format_version"] + [fn for (fn, _) in all_fields]
    for field_name in field_names:
        info = rd_class.model_fields[field_name]
        md += (
            "\n"
            + Field(
                (field_name,),
                info,
                footnotes=footnotes,
                rd_class=rd_class,
                all_examples=all_examples,
            ).get_md()
        )

    md += "\n"
    for i, full in enumerate(footnotes, start=1):
        md += f"\n[^{i}]: {full}"

    if all_examples:
        md += "# Example values\n"
        for name, examples in all_examples:
            if len(examples) == 1:
                formatted_examples = str(examples[0])
            else:
                formatted_examples = "".join(f"- {ex}\n" for ex in examples)

            md += f"### {name}\n{formatted_examples}\n"

    if footnotes:
        md += "\n"

    for file_path in [
        folder / get_documentation_file_name(rd_class, minor=True),
        folder / get_documentation_file_name(rd_class),
    ]:
        _ = file_path.write_text(md, encoding="utf-8")
        print(f"written {file_path}")

    return file_path  # type: ignore


def export_module_documentations(folder: Path, module: ModuleType):
    rd_name = to_pascal(module.__name__.split(".")[-1]) + "Descr"

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
    shutil.copy(
        str(latest), folder / get_documentation_file_name(rd_class, latest=True)
    )
    print(f" copied {latest} as latest")


def main(dist: Path):
    dist.mkdir(exist_ok=True, parents=True)

    export_module_documentations(dist, application)
    export_module_documentations(dist, dataset)
    export_module_documentations(dist, generic)
    export_module_documentations(dist, model)
    export_module_documentations(dist, notebook)


def parse_args():
    p = ArgumentParser(
        description="script that generates bioimageio user documentation"
    )
    _ = p.add_argument(
        "--dist",
        nargs="?",
        default=str((Path(__file__).parent / "../user_docs").resolve()),
    )
    args = p.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(dist=Path(args.dist))
