# autogen: start
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_2 as v0_2, v0_3 as v0_3
from .v0_3 import NotebookDescr as NotebookDescr

AnyNotebookDescr = Annotated[Union[v0_2.NotebookDescr, v0_3.NotebookDescr], Discriminator("format_version")]
# autogen: stop
