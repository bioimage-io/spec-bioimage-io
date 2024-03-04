# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- generic v0_2: `bioimageio.spec.generic.v0_2.GenericDescr` [user documentation](../../../user_docs/generic_descr_v0-2.md)
- generic v0_3: `bioimageio.spec.generic.v0_3.GenericDescr` [user documentation](../../../user_docs/generic_descr_v0-3.md)
"""
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from .v0_2 import GenericDescr as GenericDescr_v0_2
from .v0_3 import GenericDescr as GenericDescr
from .v0_3 import GenericDescr as GenericDescr_v0_3

AnyGenericDescr = Annotated[
    Union[GenericDescr_v0_2, GenericDescr_v0_3], Discriminator("format_version")
]
"""Union of any released generic desription"""
# autogen: stop
