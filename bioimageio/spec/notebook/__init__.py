# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- notebook v0_2: `bioimageio.spec.notebook.v0_2.NotebookDescr`
- notebook v0_3: `bioimageio.spec.notebook.v0_3.NotebookDescr`
"""

from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_2, v0_3

NotebookDescr = v0_3.NotebookDescr
NotebookDescr_v0_2 = v0_2.NotebookDescr
NotebookDescr_v0_3 = v0_3.NotebookDescr

AnyNotebookDescr = Annotated[
    Union[NotebookDescr_v0_2, NotebookDescr_v0_3], Discriminator("format_version")
]
"""Union of any released notebook desription"""
# autogen: stop
