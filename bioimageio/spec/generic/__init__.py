# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- generic v0_2: `bioimageio.spec.generic.v0_2.GenericDescr` [user documentation](../../../user_docs/generic_descr_v0-2.md)
- generic v0_3: `bioimageio.spec.generic.v0_3.GenericDescr` [user documentation](../../../user_docs/generic_descr_v0-3.md)
"""
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_2 as v0_2, v0_3 as v0_3
from .v0_3 import GenericDescr as GenericDescr

AnyGenericDescr = Annotated[
    Union[v0_2.GenericDescr, v0_3.GenericDescr], Discriminator("format_version")
]
"""Union of any released generic desription"""
# autogen: stop
