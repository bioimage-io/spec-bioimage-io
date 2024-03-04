# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- application v0_2: `bioimageio.spec.application.v0_2.ApplicationDescr` [user documentation](../../../user_docs/application_descr_v0-2.md)
- application v0_3: `bioimageio.spec.application.v0_3.ApplicationDescr` [user documentation](../../../user_docs/application_descr_v0-3.md)
"""
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from .v0_2 import ApplicationDescr as ApplicationDescr_v0_2
from .v0_3 import ApplicationDescr as ApplicationDescr
from .v0_3 import ApplicationDescr as ApplicationDescr_v0_3

AnyApplicationDescr = Annotated[
    Union[ApplicationDescr_v0_2, ApplicationDescr_v0_3], Discriminator("format_version")
]
"""Union of any released application desription"""
# autogen: stop
