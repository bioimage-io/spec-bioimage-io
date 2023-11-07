from typing import Literal, Optional

from pydantic import Field
from typing_extensions import Annotated

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.types import DatasetId as DatasetId
from bioimageio.spec._internal.types import FileSource as FileSource
from bioimageio.spec.generic.v0_2 import Attachments as Attachments
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import Badge as Badge
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import GenericBase, WithGenericFormatVersion
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer


class Dataset(GenericBase, WithGenericFormatVersion, title="bioimage.io dataset specification"):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    type: Literal["dataset"] = "dataset"

    source: Annotated[Optional[FileSource], Field(description="URL or path to the source of the dataset.")] = None
    """The primary source of the dataset"""


class LinkedDataset(Node):
    """Reference to a bioimage.io dataset."""

    id: DatasetId
    """A valid dataset `id` from the bioimage.io collection."""
