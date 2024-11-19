# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- application v0_2: `bioimageio.spec.application.v0_2.ApplicationDescr`
- application v0_3: `bioimageio.spec.application.v0_3.ApplicationDescr`
"""

from typing import Union

from pydantic import Discriminator, Field
from typing_extensions import Annotated

from . import v0_2, v0_3

ApplicationDescr = v0_3.ApplicationDescr
ApplicationDescr_v0_2 = v0_2.ApplicationDescr
ApplicationDescr_v0_3 = v0_3.ApplicationDescr

AnyApplicationDescr = Annotated[
    Union[
        Annotated[ApplicationDescr_v0_2, Field(title="application 0.2")],
        Annotated[ApplicationDescr_v0_3, Field(title="application 0.3")],
    ],
    Discriminator("format_version"),
    Field(title="application"),
]
"""Union of any released application desription"""
# autogen: stop
