from typing import Literal

from pydantic import HttpUrl as HttpUrl
from typing_extensions import Annotated

from bioimageio.spec._internal.types import FileSource
from bioimageio.spec._internal.types import RelativeFilePath as RelativeFilePath
from bioimageio.spec._internal.types.field_validation import WithSuffix
from bioimageio.spec.generic.v0_3 import Attachment as Attachment
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import Badge as Badge
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import GenericBase
from bioimageio.spec.generic.v0_3 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer


class Notebook(GenericBase, frozen=True, title="bioimage.io notebook specification"):
    """Bioimage.io description of a Jupyter notebook."""

    type: Literal["notebook"] = "notebook"

    source: Annotated[FileSource, WithSuffix(".ipynb", case_sensitive=True)]
    """The Jupyter notebook"""
