from typing import Annotated, Literal, Union

from pydantic import ConfigDict, Field
from bioimageio.spec.dataset import v0_2

from bioimageio.spec.generic.v0_3 import (
    LinkedResource,
    GenericBase,
)
from bioimageio.spec.shared.types import NonEmpty

__all__ = ["Dataset", "LinkedDataset", "AnyDataset"]


class Dataset(GenericBase):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    model_config = ConfigDict(
        {
            **GenericBase.model_config,
            **ConfigDict(title="bioimage.io dataset specification"),
        }
    )
    type: Literal["dataset"] = "dataset"


AnyDataset = Annotated[Union[v0_2.Dataset, Dataset], Field(discriminator="format_version")]


class LinkedDataset(LinkedResource):
    """Reference to a bioimage.io dataset."""

    id: NonEmpty[str]
    """A valid dataset `id` from the bioimage.io collection."""
