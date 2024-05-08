from pathlib import Path
from typing import Any, ClassVar, Type

from annotated_types import Predicate
from pydantic import DirectoryPath, FilePath, RootModel, StringConstraints
from typing_extensions import Annotated

from .validated_string import ValidatedString

FileName = str
AbsoluteDirectory = Annotated[DirectoryPath, Predicate(Path.is_absolute)]
AbsoluteFilePath = Annotated[FilePath, Predicate(Path.is_absolute)]

BIOIMAGEIO_YAML = "bioimageio.yaml"
ALTERNATIVE_BIOIMAGEIO_YAML_NAMES = ("rdf.yaml", "model.yaml")
ALL_BIOIMAGEIO_YAML_NAMES = (BIOIMAGEIO_YAML,) + ALTERNATIVE_BIOIMAGEIO_YAML_NAMES


class Sha256(ValidatedString):
    """SHA-256 hash value"""

    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True, to_lower=True, min_length=64, max_length=64
            ),
        ]
    ]
