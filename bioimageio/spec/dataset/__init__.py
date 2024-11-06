# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- dataset v0_2: `bioimageio.spec.dataset.v0_2.DatasetDescr`
- dataset v0_3: `bioimageio.spec.dataset.v0_3.DatasetDescr`
"""

from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_2, v0_3

DatasetDescr = v0_3.DatasetDescr
DatasetDescr_v0_2 = v0_2.DatasetDescr
DatasetDescr_v0_3 = v0_3.DatasetDescr

AnyDatasetDescr = Annotated[
    Union[DatasetDescr_v0_2, DatasetDescr_v0_3], Discriminator("format_version")
]
"""Union of any released dataset desription"""
# autogen: stop
