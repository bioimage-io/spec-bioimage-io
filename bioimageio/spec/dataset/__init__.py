# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- dataset v0_2: `bioimageio.spec.dataset.v0_2.DatasetDescr` [user documentation](../../../user_docs/dataset_descr_v0-2.md)
- dataset v0_3: `bioimageio.spec.dataset.v0_3.DatasetDescr` [user documentation](../../../user_docs/dataset_descr_v0-3.md)
"""
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_2 as v0_2, v0_3 as v0_3
from .v0_3 import DatasetDescr as DatasetDescr

AnyDatasetDescr = Annotated[
    Union[v0_2.DatasetDescr, v0_3.DatasetDescr], Discriminator("format_version")
]
"""Union of any released dataset desription"""
# autogen: stop
