import dataclasses
import inspect
from pathlib import Path
from typing import List, Tuple, Type

import bioimageio.spec.model
from bioimageio.spec.shared.schema import SharedProcessingSchema
from bioimageio.spec.shared.utils import get_ref_url, resolve_bioimageio_descrcription, snake_case_to_camel_case

REFERENCE_IMPLEMENTATIONS_SOURCE = "https://github.com/bioimage-io/core-bioimage-io-python/blob/main/bioimageio/core/prediction_pipeline/_processing.py"


@dataclasses.dataclass
class Kwarg:
    name: str
    optional: bool
    description: str


@dataclasses.dataclass
class ProcessingDocNode:
    name: str
    description: str
    kwargs: List[Kwarg]
    reference_implemation: str


@dataclasses.dataclass
class PreprocessingDocNode(ProcessingDocNode):
    prefix = "pre"


@dataclasses.dataclass
class PostprocessingDocNode(ProcessingDocNode):
    prefix = "post"


def get_docs(schema) -> Tuple[List[PreprocessingDocNode], List[PostprocessingDocNode]]:
    """retrieve docs for pre- and postprocessing from schema definitions

    using that pre- and postprocessings are defined as member classes that inherit from SharedProcessingSchema
    """

    def get_kwargs_doc(Sch: Type[SharedProcessingSchema]) -> List[Kwarg]:
        return sorted(
            [
                Kwarg(
                    name=name,
                    optional=not f.required or bool(f.missing),
                    description=resolve_bioimageio_descrcription(f.bioimageio_description),
                )
                for name, f in Sch().fields.items()
            ],
            key=lambda kw: (kw.optional, kw.name),
        )

    preps = [
        PreprocessingDocNode(
            name=name,
            description=resolve_bioimageio_descrcription(member.bioimageio_description),
            kwargs=get_kwargs_doc(member),
            reference_implemation=get_ref_url(
                "class", snake_case_to_camel_case(name), REFERENCE_IMPLEMENTATIONS_SOURCE
            ),
        )
        for name, member in inspect.getmembers(schema.Preprocessing)
        if inspect.isclass(member) and issubclass(member, SharedProcessingSchema)
    ]
    posts = [
        PostprocessingDocNode(
            name=name,
            description=resolve_bioimageio_descrcription(member.bioimageio_description),
            kwargs=get_kwargs_doc(member),
            reference_implemation=get_ref_url(
                "class", snake_case_to_camel_case(name), REFERENCE_IMPLEMENTATIONS_SOURCE
            ),
        )
        for name, member in inspect.getmembers(schema.Postprocessing)
        if inspect.isclass(member) and issubclass(member, SharedProcessingSchema)
    ]
    return preps, posts


def markdown_from_docs(doc_nodes: List[ProcessingDocNode], title: str, description: str):
    md = f"# {title}\n{description}\n"

    for doc in doc_nodes:
        md += f"### `{doc.name}`\n{doc.description}\n"
        if doc.kwargs:
            md += f"- key word arguments:\n"
            for kwarg in doc.kwargs:
                md += f"  - `{'[' if kwarg.optional else ''}{kwarg.name}{']' if kwarg.optional else ''}` {kwarg.description}\n"
        md += f"- reference implementation: {doc.reference_implemation}\n"

    return md


def export_markdown_docs(folder: Path, spec) -> None:
    model_or_version = spec.__name__.split(".")[-1]
    format_version_wo_patch = ".".join(spec.format_version.split(".")[:2])
    if model_or_version == "model":
        format_version_file_name = "latest"
    else:
        format_version_file_name = format_version_wo_patch.replace(".", "_")

    for docs in get_docs(spec.schema):
        assert isinstance(docs, list)
        prefix = docs[0].prefix
        md = markdown_from_docs(
            docs,
            title=f"{prefix.title()}processing operations in model spec {format_version_wo_patch}",
            description=(
                f"The supported operations that are valid in {prefix}processing. "
                "IMPORTANT: these operations must return float32 tensors, so that their output can be consumed by the "
                "models."
            ),
        )
        path = folder / f"{prefix}processing_spec_{format_version_file_name}.md"
        path.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    import bioimageio.spec.model.v0_3

    dist = Path(__file__).parent / "../dist"
    dist.mkdir(exist_ok=True)

    export_markdown_docs(dist, bioimageio.spec.model.v0_4)
    export_markdown_docs(dist, bioimageio.spec.model.v0_3)
    export_markdown_docs(dist, bioimageio.spec.model)
