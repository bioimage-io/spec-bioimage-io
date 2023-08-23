from typing import Union

from pydantic import Field
from typing_extensions import Annotated

from bioimageio.spec import application, collection, dataset, generic, model, notebook

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


SpecificResourceDescription = Annotated[
    Union[
        application.AnyApplication,
        collection.AnyCollection,
        dataset.AnyDataset,
        model.AnyModel,
        notebook.AnyNotebook,
    ],
    Field(discriminator="type"),
]
"""Any of the implemented, non-generic resource descriptions"""

ResourceDescription = Union[
    SpecificResourceDescription,
    generic.AnyGeneric,
]
"""Any of the implemented resource descriptions"""
