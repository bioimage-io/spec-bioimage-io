# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- dataset v0_2: `bioimageio.spec.dataset.v0_2.DatasetDescr` [user documentation](../../../user_docs/dataset_descr_v0-2.md)
- dataset v0_3: `bioimageio.spec.dataset.v0_3.DatasetDescr` [user documentation](../../../user_docs/dataset_descr_v0-3.md)
"""
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from .v0_2 import DatasetDescr as DatasetDescr_v0_2
from .v0_3 import DatasetDescr as DatasetDescr
from .v0_3 import DatasetDescr as DatasetDescr_v0_3

AnyDatasetDescr = Annotated[
    Union[DatasetDescr_v0_2, DatasetDescr_v0_3], Discriminator("format_version")
]
"""Union of any released dataset desription"""
# autogen: stop
