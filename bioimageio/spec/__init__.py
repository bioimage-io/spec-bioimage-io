import json
import pathlib
from typing import Union

from typing_extensions import Annotated

from bioimageio.spec import application, collection, dataset, generic, model, notebook, shared
from bioimageio.spec._internal._utils import Field

__all__ = (
    "__version__",
    "collection",
    "dataset",
    "generic",
    "model",
    "LatestResourceDescription",
    "ResourceDescription",
    "shared",
    "LatestSpecificResourceDescription",
    "SpecificResourceDescription",
)

with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__: str = json.load(f)["version"]
    assert isinstance(__version__, str)

LatestSpecificResourceDescription = Annotated[
    Union[
        application.Application,
        collection.Collection,
        dataset.Dataset,
        model.Model,
        notebook.Notebook,
    ],
    Field(discriminator="type"),
]
"""A specific resource description following the latest specification format.
Loading previous format versions is allowed where automatic updating is possible. (e.g. renaming of a field)"""

LatestResourceDescription = Union[LatestSpecificResourceDescription, generic.Generic]
"""A specific or generic resource description following the latest specification format
Loading previous format versions is allowed where automatic updating is possible. (e.g. renaming of a field)"""

SpecificResourceDescription = Annotated[
    Union[
        application.v0_2.Application,
        collection.v0_2.Collection,
        dataset.v0_2.Dataset,
        model.v0_4.Model,
        # Annotated[Union[model.v0_4.Model, model.v0_5.Model], Field(discriminator="format_version")],
        notebook.v0_2.Notebook,
    ],
    Field(discriminator="type"),
]
"""A specific resource description.
Previous format versions are not converted upon loading (except for patch/micro format version changes)."""

ResourceDescription = Union[SpecificResourceDescription, generic.v0_2.Generic]
"""A specific or generic resource description.
Previous format versions are not converted upon loading (except for patch/micro format version changes)."""
