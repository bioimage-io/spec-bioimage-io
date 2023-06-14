from typing import Literal
from ..general.v0_2 import ResourceDescriptionBase, LatestFormatVersion, FormatVersion, LATEST_FORMAT_VERSION


__all__ = ["Dataset", "LatestFormatVersion", "FormatVersion", "LATEST_FORMAT_VERSION"]


class Dataset(ResourceDescriptionBase):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    model_config = {
        **ResourceDescriptionBase.model_config,
        **dict(title=f"bioimage.io Dataset RDF {LATEST_FORMAT_VERSION}"),
    }
    type: Literal["dataset"] = "dataset"
