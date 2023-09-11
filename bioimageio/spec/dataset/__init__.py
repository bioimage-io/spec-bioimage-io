# autogen: start
from typing import Union

from pydantic import Field
from typing_extensions import Annotated

from . import v0_2 as v0_2, v0_3 as v0_3
from .v0_3 import Dataset as Dataset

AnyDataset = Annotated[Union[v0_2.Dataset, v0_3.Dataset], Field(discriminator="format_version")]
# autogen: stop
