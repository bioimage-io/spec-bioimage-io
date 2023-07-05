from typing import Literal
from bioimageio.spec.generic.v0_2 import LatestFormatVersion, ResourceDescriptionBase, LATEST_FORMAT_VERSION


class Notebook(ResourceDescriptionBase):
    """Bioimage.io description of a Jupyter Notebook."""

    model_config = {
        **ResourceDescriptionBase.model_config,
        **dict(title=f"bioimage.io generic RDF {LATEST_FORMAT_VERSION} used to describe notebooks"),
    }
    """pydantic model_config"""

    format_version: LatestFormatVersion = LATEST_FORMAT_VERSION

    type: Literal["notebook"] = "notebook"
