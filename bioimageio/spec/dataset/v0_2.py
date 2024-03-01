from typing import Literal, Optional

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.io_basics import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec._internal.types import DatasetId as DatasetId
from bioimageio.spec.generic.v0_2 import AttachmentsDescr as AttachmentsDescr
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import Doi as Doi
from bioimageio.spec.generic.v0_2 import GenericDescrBase
from bioimageio.spec.generic.v0_2 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_2 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_2 import OrcidId as OrcidId
from bioimageio.spec.generic.v0_2 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_2 import ResourceId as ResourceId
from bioimageio.spec.generic.v0_2 import Uploader as Uploader


class DatasetDescr(GenericDescrBase, title="bioimage.io dataset specification"):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    type: Literal["dataset"] = "dataset"

    id: Optional[DatasetId] = None
    """Model zoo (bioimage.io) wide, unique identifier (assigned by bioimage.io)"""

    source: Optional[HttpUrl] = None
    """"URL to the source of the dataset."""


class LinkedDataset(Node):
    """Reference to a bioimage.io dataset."""

    id: DatasetId
    """A valid dataset `id` from the bioimage.io collection."""

    version_nr: Optional[int] = None
    """version number (n-th published version, not the semantic version) of linked dataset"""
