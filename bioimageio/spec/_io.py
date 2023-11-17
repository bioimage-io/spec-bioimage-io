from typing import Literal, TextIO, Union, cast

from pydantic import FilePath, NewPath

from bioimageio.spec import ResourceDescription
from bioimageio.spec._description import InvalidDescription, build_description, dump_description
from bioimageio.spec._internal.base_nodes import ResourceDescriptionBase
from bioimageio.spec._internal.constants import DISCOVER
from bioimageio.spec._internal.io_utils import open_bioimageio_yaml, write_yaml
from bioimageio.spec._internal.types import (
    BioimageioYamlContent,
    FileSource,
    YamlValue,
)
from bioimageio.spec._internal.validation_context import ValidationContext


def load_description(
    source: FileSource,
    /,
    *,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
) -> Union[ResourceDescription, InvalidDescription]:
    opened = open_bioimageio_yaml(source)

    return build_description(
        opened.content,
        context=ValidationContext(root=opened.original_root, file_name=opened.original_file_name),
        format_version=format_version,
    )


def save_bioimageio_yaml_only(
    rd: Union[ResourceDescription, BioimageioYamlContent], /, file: Union[NewPath, FilePath, TextIO]
):
    if isinstance(rd, ResourceDescriptionBase):
        content = dump_description(rd)
    else:
        content = rd

    write_yaml(cast(YamlValue, content), file)
