import os
from typing import Union

from marshmallow import ValidationError

from bioimageio.spec.shared import resolve_source
from bioimageio.spec.shared.raw_nodes import URI


def validate_markdown(md_source, *, field_name: str, root: Union[os.PathLike, URI]):
    doc_path = resolve_source(md_source, root_path=root)
    with doc_path.open() as f:
        raw_doc: str = f.readline()

    if not raw_doc.startswith("#"):
        raise ValidationError(
            f"Please start the {field_name} Markdown file with a heading, e.g. '# My Model Docuemntation'.", field_name
        )
