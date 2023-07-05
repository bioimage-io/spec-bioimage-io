from typing import Literal
from bioimageio.spec.generic.v0_2 import LatestFormatVersion, ResourceDescriptionBase, LATEST_FORMAT_VERSION


class Application(ResourceDescriptionBase):
    """Bioimage.io description of an application."""

    model_config = {
        **ResourceDescriptionBase.model_config,
        **dict(title=f"bioimage.io generic RDF {LATEST_FORMAT_VERSION} used to describe applications"),
    }
    """pydantic model_config"""

    format_version: LatestFormatVersion = LATEST_FORMAT_VERSION

    type: Literal["application"] = "application"
