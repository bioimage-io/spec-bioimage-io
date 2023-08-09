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
)


with files("bioimageio.spec").joinpath("VERSION").open("r", encoding="utf-8") as f:
    # with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__: str = json.load(f)["version"]
    assert isinstance(__version__, str)

ResourceDescription_v0_3 = Union[
    Annotated[
        Union[
            application.v0_3.Application,
            collection.v0_3.Collection,
            dataset.v0_3.Dataset,
            model.v0_5.Model,
            notebook.v0_3.Notebook,
        ],
        Field(discriminator="type"),
    ],
    generic.v0_3.Generic,
]
"""A resource description following the 0.3.x (model: 0.5.x) specification format"""

LatestResourceDescription = ResourceDescription_v0_3
"""A resource description following the latest specification format"""


ResourceDescription_v0_2 = Union[
    Annotated[
        Union[
            application.v0_2.Application,
            collection.v0_2.Collection,
            dataset.v0_2.Dataset,
            model.v0_4.Model,
            notebook.v0_2.Notebook,
        ],
        Field(discriminator="type"),
    ],
    generic.v0_2.Generic,
]
"""A resource description following the 0.2.x (model: 0.4.x) specification format"""


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
"""Any of the implemented, non-generic resource descriptions"""

ResourceDescription = Union[
    SpecificResourceDescription,
    AnyGeneric,
]
"""Any of the implemented resource descriptions"""
