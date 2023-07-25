import json
from importlib.resources import files
from typing import Union

from typing_extensions import Annotated

from bioimageio.spec import application, collection, dataset, generic, model, notebook, shared
from bioimageio.spec._internal._utils import Field
from bioimageio.spec.application import AnyApplication, Application
from bioimageio.spec.collection import AnyCollection, Collection
from bioimageio.spec.dataset import AnyDataset, Dataset
from bioimageio.spec.generic import AnyGeneric, Generic
from bioimageio.spec.model import AnyModel, Model
from bioimageio.spec.notebook import AnyNotebook, Notebook

__all__ = (
    "__version__",
    "application",
    "Application",
    "AnyApplication",
    "collection",
    "Collection",
    "AnyCollection",
    "dataset",
    "Dataset",
    "AnyDataset",
    "generic",
    "Generic",
    "AnyGeneric",
    "model",
    "Model",
    "AnyModel",
    "notebook",
    "Notebook",
    "AnyNotebook",
    "LatestResourceDescription",
    "ResourceDescription",
    "shared",
    "LatestSpecificResourceDescription",
    "SpecificResourceDescription",
)


with files("bioimageio.spec").joinpath("VERSION").open("r", encoding="utf-8") as f:
    # with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__: str = json.load(f)["version"]
    assert isinstance(__version__, str)

LatestSpecificResourceDescription = Annotated[
    Union[
        Application,
        Collection,
        Dataset,
        Model,
        Notebook,
    ],
    Field(discriminator="type"),
]
"""A specific resource description following the latest specification format.
Loading previous format versions is allowed where automatic updating is possible. (e.g. renaming of a field)"""

LatestResourceDescription = Union[LatestSpecificResourceDescription, Generic]
"""A specific or generic resource description following the latest specification format
Loading previous format versions is allowed where automatic updating is possible. (e.g. renaming of a field)"""

SpecificResourceDescription = Annotated[
    Union[
        AnyApplication,
        AnyCollection,
        AnyDataset,
        AnyModel,
        AnyNotebook,
    ],
    Field(discriminator="type"),
]
"""A specific resource description.
Previous format versions are not converted upon loading (except for patch/micro format version changes)."""

ResourceDescription = Union[SpecificResourceDescription, AnyGeneric]
"""A specific or generic resource description.
Previous format versions are not converted upon loading (except for patch/micro format version changes)."""
