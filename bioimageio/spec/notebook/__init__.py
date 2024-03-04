# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- notebook v0_2: `bioimageio.spec.notebook.v0_2.NotebookDescr` [user documentation](../../../user_docs/notebook_descr_v0-2.md)
- notebook v0_3: `bioimageio.spec.notebook.v0_3.NotebookDescr` [user documentation](../../../user_docs/notebook_descr_v0-3.md)
"""
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from .v0_2 import NotebookDescr as NotebookDescr_v0_2
from .v0_3 import NotebookDescr as NotebookDescr
from .v0_3 import NotebookDescr as NotebookDescr_v0_3

AnyNotebookDescr = Annotated[
    Union[NotebookDescr_v0_2, NotebookDescr_v0_3], Discriminator("format_version")
]
"""Union of any released notebook desription"""
# autogen: stop
