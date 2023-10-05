from typing import Literal

from typing_extensions import Annotated

from bioimageio.spec._internal.types import FileSource
from bioimageio.spec._internal.types.field_validation import WithSuffix
from bioimageio.spec.generic.v0_2 import Attachments as Attachments
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import Badge as Badge
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import GenericBase
from bioimageio.spec.generic.v0_2 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer


class Notebook(GenericBase, frozen=True, title="bioimage.io notebook specification"):
    """Bioimage.io description of a Jupyter Notebook."""

    type: Literal["notebook"] = "notebook"

    source: Annotated[FileSource, WithSuffix(".ipynb", case_sensitive=True)]
    """The Jupyter notebook"""
