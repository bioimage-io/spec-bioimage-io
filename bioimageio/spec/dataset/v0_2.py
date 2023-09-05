from typing import Literal

from bioimageio.spec._internal.types import NonEmpty
from bioimageio.spec.generic.v0_2 import *
from bioimageio.spec.generic.v0_2 import GenericBase

__all__ = [
    "Attachments",
    "Author",
    "Badge",
    "CiteEntry",
    "Dataset",
    "LinkedDataset",
    "LinkedResource",
    "Maintainer",
]


class Dataset(GenericBase, frozen=True, title="bioimage.io dataset specification"):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    type: Literal["dataset"] = "dataset"


class LinkedDataset(LinkedResource, frozen=True):
    """Reference to a bioimage.io dataset."""

    id: NonEmpty[str]
    """A valid dataset `id` from the bioimage.io collection."""
