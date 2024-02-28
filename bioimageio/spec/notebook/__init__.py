# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- notebook v0_2: `bioimageio.spec.notebook.v0_2.NotebookDescr` [user documentation](../../../user_docs/notebook_descr_v0-2.md)
- notebook v0_3: `bioimageio.spec.notebook.v0_3.NotebookDescr` [user documentation](../../../user_docs/notebook_descr_v0-3.md)
"""
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_2 as v0_2, v0_3 as v0_3
from .v0_3 import NotebookDescr as NotebookDescr

AnyNotebookDescr = Annotated[
    Union[v0_2.NotebookDescr, v0_3.NotebookDescr], Discriminator("format_version")
]
"""Union of any released notebook desription"""
# autogen: stop
