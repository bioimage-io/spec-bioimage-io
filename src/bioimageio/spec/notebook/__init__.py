# autogen: start
"""notebook resource description format

Implementations of all released minor versions are available in submodules.
"""

from typing import Union

from pydantic import Discriminator, Field
from typing_extensions import Annotated

from . import v0_2, v0_3

NotebookDescr = v0_3.NotebookDescr
NotebookDescr_v0_2 = v0_2.NotebookDescr
NotebookDescr_v0_3 = v0_3.NotebookDescr

AnyNotebookDescr = Annotated[
    Union[
        Annotated[NotebookDescr_v0_2, Field(title="notebook 0.2")],
        Annotated[NotebookDescr_v0_3, Field(title="notebook 0.3")],
    ],
    Discriminator("format_version"),
    Field(title="notebook"),
]
"""Union of any released notebook desription"""
# autogen: stop
