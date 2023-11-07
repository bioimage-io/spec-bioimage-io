from typing import Literal

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.types import DatasetId
from bioimageio.spec.generic.v0_3 import Attachment as Attachment
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import Badge as Badge
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import GenericBase, WithGenericFormatVersion
from bioimageio.spec.generic.v0_3 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3 import RelativeFilePath as RelativeFilePath


class Dataset(GenericBase, WithGenericFormatVersion, title="bioimage.io dataset specification"):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    type: Literal["dataset"] = "dataset"


class LinkedDataset(Node):
    """Reference to a bioimage.io dataset."""

    id: DatasetId
    """A valid dataset `id` from the bioimage.io collection."""
