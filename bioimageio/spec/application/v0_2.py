from typing import Literal

from bioimageio.spec.generic.v0_2 import *
from bioimageio.spec.generic.v0_2 import GenericBase

__all__ = [
    "Application",
    "Attachments",
    "Author",
    "Badge",
    "CiteEntry",
    "LinkedResource",
    "Maintainer",
]


class Application(GenericBase, frozen=True, title="bioimage.io application specification"):
    """Bioimage.io description of an application."""

    type: Literal["application"] = "application"
