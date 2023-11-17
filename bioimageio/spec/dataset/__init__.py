# autogen: start
from typing import Union

from pydantic import Field
from typing_extensions import Annotated

from . import v0_2 as v0_2, v0_3 as v0_3
from .v0_3 import DatasetDescr as DatasetDescr

AnyDatasetDescr = Annotated[Union[v0_2.DatasetDescr, v0_3.DatasetDescr], Field(discriminator="format_version")]
# autogen: stop
