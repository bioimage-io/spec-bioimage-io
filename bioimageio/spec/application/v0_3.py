from typing import Literal

from pydantic import ConfigDict

from bioimageio.spec.generic.v0_3 import *
from bioimageio.spec.generic.v0_3 import GenericBase

__all__ = [
    "Application",
    "Attachments",
    "Author",
    "Badge",
    "CiteEntry",
    "LinkedResource",
    "Maintainer",
]


class Application(GenericBase):
    """Bioimage.io description of an application."""

    model_config = ConfigDict(
        {**GenericBase.model_config, **ConfigDict(title="bioimage.io application specification")},
    )
    """pydantic model_config"""

    type: Literal["application"] = "application"
