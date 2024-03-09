from pathlib import Path

from annotated_types import Predicate
from pydantic import DirectoryPath, FilePath
from typing_extensions import Annotated

FileName = str
AbsoluteDirectory = Annotated[DirectoryPath, Predicate(Path.is_absolute)]
AbsoluteFilePath = Annotated[FilePath, Predicate(Path.is_absolute)]

BIOIMAGEIO_YAML = "rdf.yaml"
ALTERNATIVE_BIOIMAGEIO_YAML_NAMES = ("bioimageio.yaml", "model.yaml")
ALL_BIOIMAGEIO_YAML_NAMES = (BIOIMAGEIO_YAML,) + ALTERNATIVE_BIOIMAGEIO_YAML_NAMES
