import json
import pathlib
from typing import Union

from typing_extensions import Annotated

from bioimageio.spec import collection, dataset, generic, model, shared
from bioimageio.spec._internal.utils import Field

__all__ = [
    "__version__",
    "collection",
    "generic",
    "model",
    "shared",
    "dataset",
    "KnownResourceDescription",
    "ResourceDescription",
]

with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__ = json.load(f)["version"]

KnownResourceDescription = Annotated[
    Union[
        notebook.v0_2.Notebook,
        application.v0_2.Application,
        collection.v0_2.Collection,
        dataset.v0_2.Dataset,
        model.v0_4.Model,
        # model.v0_5.Model,
    ],
    Field(discriminator="type"),
]
ResourceDescription = Union[KnownResourceDescription, generic.v0_2.Generic]
