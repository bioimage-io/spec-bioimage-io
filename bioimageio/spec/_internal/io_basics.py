from pathlib import Path
from typing import Any, ClassVar, Type

import pydantic
import zipp
from annotated_types import Predicate
from pydantic import RootModel, StringConstraints
from typing_extensions import Annotated

from .validated_string import ValidatedString

FileName = str
FilePath = Annotated[pydantic.FilePath, pydantic.Field(title="FilePath")]
AbsoluteDirectory = Annotated[
    pydantic.DirectoryPath,
    Predicate(Path.is_absolute),
    pydantic.Field(title="AbsoluteDirectory"),
]
AbsoluteFilePath = Annotated[
    pydantic.FilePath,
    Predicate(Path.is_absolute),
    pydantic.Field(title="AbsoluteFilePath"),
]

BIOIMAGEIO_YAML = "rdf.yaml"
ALTERNATIVE_BIOIMAGEIO_YAML_NAMES = ("bioimageio.yaml", "model.yaml")
ALL_BIOIMAGEIO_YAML_NAMES = (BIOIMAGEIO_YAML,) + ALTERNATIVE_BIOIMAGEIO_YAML_NAMES

ZipPath = zipp.Path  # not zipfile.Path due to https://bugs.python.org/issue40564


class Sha256(ValidatedString):
    """A SHA-256 hash value"""

    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True, to_lower=True, min_length=64, max_length=64
            ),
        ]
    ]
