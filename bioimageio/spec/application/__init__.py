# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- application v0_2: `bioimageio.spec.application.v0_2.ApplicationDescr`
- application v0_3: `bioimageio.spec.application.v0_3.ApplicationDescr`
"""

from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_2, v0_3

ApplicationDescr = v0_3.ApplicationDescr
ApplicationDescr_v0_2 = v0_2.ApplicationDescr
ApplicationDescr_v0_3 = v0_3.ApplicationDescr

AnyApplicationDescr = Annotated[
    Union[ApplicationDescr_v0_2, ApplicationDescr_v0_3], Discriminator("format_version")
]
"""Union of any released application desription"""
# autogen: stop
