from typing import Literal

from bioimageio.spec.generic.v0_2 import GenericBase


class Application(GenericBase):
    """Bioimage.io description of an application."""

    model_config = {
        **GenericBase.model_config,
        **dict(title="bioimage.io application specification"),
    }
    """pydantic model_config"""

    type: Literal["application"] = "application"
