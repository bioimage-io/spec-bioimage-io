from typing import Literal, Union

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from bioimageio.spec.application import v0_2
from bioimageio.spec.generic.v0_3 import GenericBase


class Application(GenericBase):
    """Bioimage.io description of an application."""

    model_config = ConfigDict(
        {**GenericBase.model_config, **ConfigDict(title="bioimage.io application specification")},
    )
    """pydantic model_config"""

    type: Literal["application"] = "application"


AnyApplication = Annotated[Union[v0_2.Application, Application], Field(discriminator="format_version")]
