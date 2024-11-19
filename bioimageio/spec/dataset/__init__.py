# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- dataset v0_2: `bioimageio.spec.dataset.v0_2.DatasetDescr`
- dataset v0_3: `bioimageio.spec.dataset.v0_3.DatasetDescr`
"""

from typing import Union

from pydantic import Discriminator, Field
from typing_extensions import Annotated

from . import v0_2, v0_3

DatasetDescr = v0_3.DatasetDescr
DatasetDescr_v0_2 = v0_2.DatasetDescr
DatasetDescr_v0_3 = v0_3.DatasetDescr

AnyDatasetDescr = Annotated[
    Union[
        Annotated[DatasetDescr_v0_2, Field(title="dataset 0.2")],
        Annotated[DatasetDescr_v0_3, Field(title="dataset 0.3")],
    ],
    Discriminator("format_version"),
    Field(title="dataset"),
]
"""Union of any released dataset desription"""
# autogen: stop
