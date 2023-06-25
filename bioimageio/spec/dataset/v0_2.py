from typing import Literal

from bioimageio.spec.generic.v0_2 import (
    LATEST_FORMAT_VERSION,
    FormatVersion,
    LatestFormatVersion,
    LinkedResource,
    ResourceDescriptionBase,
)
from bioimageio.spec.shared.types import NonEmpty

__all__ = ["Dataset", "FormatVersion", "LATEST_FORMAT_VERSION", "LatestFormatVersion", "LinkedDataset"]


class Dataset(ResourceDescriptionBase):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    model_config = {
        **ResourceDescriptionBase.model_config,
        **dict(title=f"bioimage.io Dataset RDF {LATEST_FORMAT_VERSION}"),
    }
    type: Literal["dataset"] = "dataset"


# class DatasetId(ResourceId):

#     type = "dataset"


class LinkedDataset(LinkedResource):
    """Reference to a bioimage.io dataset."""

    id: NonEmpty[str]
    """A valid dataset `id` from the bioimage.io collection."""
