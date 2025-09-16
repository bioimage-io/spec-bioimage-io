# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- model v0_4: `bioimageio.spec.model.v0_4.ModelDescr`
- model v0_5: `bioimageio.spec.model.v0_5.ModelDescr`
"""

from typing import Union

from pydantic import Discriminator, Field
from typing_extensions import Annotated

from . import v0_4, v0_5

ModelDescr = v0_5.ModelDescr
ModelDescr_v0_4 = v0_4.ModelDescr
ModelDescr_v0_5 = v0_5.ModelDescr

AnyModelDescr = Annotated[
    Union[
        Annotated[ModelDescr_v0_4, Field(title="model 0.4")],
        Annotated[ModelDescr_v0_5, Field(title="model 0.5")],
    ],
    Discriminator("format_version"),
    Field(title="model"),
]
"""Union of any released model desription"""
# autogen: stop
