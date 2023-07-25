from typing import Literal

from pydantic import ConfigDict

from bioimageio.spec.generic.v0_2 import GenericBase


class Application(GenericBase):
    """Bioimage.io description of an application."""

    model_config = ConfigDict(
        {**GenericBase.model_config, **ConfigDict(title="bioimage.io application specification")},
    )
    """pydantic model_config"""

    type: Literal["application"] = "application"
