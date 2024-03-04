# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- model v0_4: `bioimageio.spec.model.v0_4.ModelDescr` [user documentation](../../../user_docs/model_descr_v0-4.md)
- model v0_5: `bioimageio.spec.model.v0_5.ModelDescr` [user documentation](../../../user_docs/model_descr_v0-5.md)
"""
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from .v0_4 import ModelDescr as ModelDescr_v0_4
from .v0_5 import ModelDescr as ModelDescr
from .v0_5 import ModelDescr as ModelDescr_v0_5

AnyModelDescr = Annotated[
    Union[ModelDescr_v0_4, ModelDescr_v0_5], Discriminator("format_version")
]
"""Union of any released model desription"""
# autogen: stop
