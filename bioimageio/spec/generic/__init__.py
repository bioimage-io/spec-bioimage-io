# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- generic v0_2: `bioimageio.spec.generic.v0_2.GenericDescr`
- generic v0_3: `bioimageio.spec.generic.v0_3.GenericDescr`
"""

from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_2, v0_3

GenericDescr = v0_3.GenericDescr
GenericDescr_v0_2 = v0_2.GenericDescr
GenericDescr_v0_3 = v0_3.GenericDescr

AnyGenericDescr = Annotated[
    Union[GenericDescr_v0_2, GenericDescr_v0_3], Discriminator("format_version")
]
"""Union of any released generic desription"""
# autogen: stop
