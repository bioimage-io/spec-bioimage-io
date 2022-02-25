import dataclasses
from pathlib import Path
from typing import List, Sequence, Tuple, Type

import bioimageio.spec.model
from bioimageio.spec.model.v0_3.schema import _WeightsEntryBase
from bioimageio.spec.shared.utils import resolve_bioimageio_descrcription

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore


@dataclasses.dataclass
class Kwarg:
    name: str
    description: str
    optional: bool
    maybe_optional: bool


@dataclasses.dataclass
class WeightsFormatDocNode:
    name: str
    description: str
    kwargs: List[Kwarg]


def get_doc(schema) -> Tuple[List[Kwarg], List[WeightsFormatDocNode]]:
    """retrieve documentation of weight formats from their definitions schema"""

    def get_kwargs_doc(we: Type[_WeightsEntryBase], exclude: Sequence[str] = tuple()) -> List[Kwarg]:
        return sorted(
            [
                Kwarg(
                    name=name,
                    description=resolve_bioimageio_descrcription(f.bioimageio_description),
                    optional=not f.required or bool(f.missing),
                    maybe_optional=f.bioimageio_maybe_required,
                )
                for name, f in we().fields.items()
                if name != "weights_format" and name not in exclude
            ],
            key=lambda kw: (kw.optional, kw.name),
        )

    common_kwargs = get_kwargs_doc(_WeightsEntryBase)

    def get_wf_name_from_wf_schema(wfs):
        return wfs().fields["weights_format"].validate.comparable

    return (
        common_kwargs,
        [
            WeightsFormatDocNode(
                name=get_wf_name_from_wf_schema(wfs),
                description=resolve_bioimageio_descrcription(wfs.bioimageio_description),
                kwargs=get_kwargs_doc(wfs, exclude=[kw.name for kw in common_kwargs]),
            )
            for wfs in get_args(schema.WeightsEntry)  # schema.WeightsEntry is a typing.Union of weights format schemas
        ],
    )


def get_md_kwargs(kwargs: Sequence[Kwarg], indent: int = 0):
    md = ""
    for kwarg in kwargs:
        md += (
            f"{' ' * indent}- `{kwarg.name}` _{'optional' if kwarg.optional or kwarg.maybe_optional else 'required'}"
            f"{'*' if kwarg.maybe_optional else ''}_ {kwarg.description}\n"
        )

    return md


def md_from_doc(doc_nodes: List[WeightsFormatDocNode]):
    md = ""
    for doc in doc_nodes:
        md += f"### `{doc.name}`\n{doc.description}\n"
        if doc.kwargs:
            md += f"- key word arguments:\n"
            md += get_md_kwargs(doc.kwargs, indent=2)

    return md


def export_markdown_docs(folder: Path, spec) -> None:
    model_or_version = spec.__name__.split(".")[-1]
    format_version_wo_patch = ".".join(spec.format_version.split(".")[:2])
    if model_or_version == "model":
        format_version_file_name = "latest"
    else:
        format_version_file_name = format_version_wo_patch.replace(".", "_")

    common_kwargs, doc = get_doc(spec.schema)
    md = (
        (
            f"# Weight formats in model spec {format_version_wo_patch}\n"
            "## Common key word arguments for all weight formats\n"
            "Optional arguments are marked as _optional_ or _optional*_ with an asterisk if they are optional "
            "depending on another argument's value.\n\n"
        )
        + get_md_kwargs(common_kwargs)
        + ("\n## Weight formats and their additional key word arguments\n")
    )
    md += md_from_doc(doc)
    path = folder / f"weight_formats_spec_{format_version_file_name}.md"
    path.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    import bioimageio.spec.model

    dist = Path(__file__).parent / "../dist"
    dist.mkdir(exist_ok=True)

    export_markdown_docs(dist, bioimageio.spec.model.v0_3)
    export_markdown_docs(dist, bioimageio.spec.model.v0_4)
    export_markdown_docs(dist, bioimageio.spec.model)
