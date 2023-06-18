import json
import pathlib
from typing import Annotated, Union
from bioimageio.spec.generic.v0_2 import ResourceDescriptionBase

from bioimageio.spec.shared.fields import Field

from . import collection, dataset, generic, model, shared

__all__ = [
    "__version__",
    "collection",
    "generic",
    "model",
    "shared",
    "dataset",
    "SpecializedDescription",
    "ResourceDescription",
]

with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__ = json.load(f)["version"]

SpecializedDescription = Annotated[
    Union[
        collection.v0_2.Collection,
        dataset.v0_2.Dataset,
        model.v0_4.Model,
        model.v0_5.Model,
    ],
    Field(discriminator="type"),
]
ResourceDescription = Union[SpecializedDescription, generic.v0_2.GenericDescription]
