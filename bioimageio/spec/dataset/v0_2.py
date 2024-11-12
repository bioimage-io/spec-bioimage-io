from typing import Literal, Optional

from .._internal.common_nodes import Node
from .._internal.io_basics import AbsoluteFilePath as AbsoluteFilePath
from .._internal.url import HttpUrl as HttpUrl
from ..generic.v0_2 import VALID_COVER_IMAGE_EXTENSIONS as VALID_COVER_IMAGE_EXTENSIONS
from ..generic.v0_2 import AttachmentsDescr as AttachmentsDescr
from ..generic.v0_2 import Author as Author
from ..generic.v0_2 import BadgeDescr as BadgeDescr
from ..generic.v0_2 import CiteEntry as CiteEntry
from ..generic.v0_2 import Doi as Doi
from ..generic.v0_2 import GenericDescrBase, ResourceId
from ..generic.v0_2 import LinkedResource as LinkedResource
from ..generic.v0_2 import Maintainer as Maintainer
from ..generic.v0_2 import OrcidId as OrcidId
from ..generic.v0_2 import RelativeFilePath as RelativeFilePath
from ..generic.v0_2 import Uploader as Uploader
from ..generic.v0_2 import Version as Version


class DatasetId(ResourceId):
    pass


class DatasetDescr(GenericDescrBase, title="bioimage.io dataset specification"):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    type: Literal["dataset"] = "dataset"

    id: Optional[DatasetId] = None
    """bioimage.io-wide unique resource identifier
    assigned by bioimage.io; version **un**specific."""

    source: Optional[HttpUrl] = None
    """"URL to the source of the dataset."""


class LinkedDataset(Node):
    """Reference to a bioimage.io dataset."""

    id: DatasetId
    """A valid dataset `id` from the bioimage.io collection."""

    version_number: Optional[int] = None
    """version number (n-th published version, not the semantic version) of linked dataset"""
