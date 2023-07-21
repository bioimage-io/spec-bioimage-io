from typing import Literal

from bioimageio.spec.generic.v0_2 import (
    LinkedResource,
    GenericBase,
)
from bioimageio.spec.shared.types import NonEmpty

__all__ = ["Dataset", "LinkedDataset"]


class Dataset(GenericBase):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    model_config = {
        **GenericBase.model_config,
        **dict(title="bioimage.io dataset specification"),
    }
    type: Literal["dataset"] = "dataset"


class LinkedDataset(LinkedResource):
    """Reference to a bioimage.io dataset."""

    id: NonEmpty[str]
    """A valid dataset `id` from the bioimage.io collection."""
