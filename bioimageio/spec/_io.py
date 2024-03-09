from typing import Literal, TextIO, Union, cast

from pydantic import FilePath, NewPath

from ._description import (
    DISCOVER,
    InvalidDescr,
    ResourceDescr,
    build_description,
    dump_description,
)
from ._internal.common_nodes import ResourceDescrBase
from ._internal.io import BioimageioYamlContent, YamlValue
from ._internal.io_utils import open_bioimageio_yaml, write_yaml
from ._internal.validation_context import ValidationContext
from .common import PermissiveFileSource
from .summary import ValidationSummary


def load_description(
    source: PermissiveFileSource,
    /,
    *,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
) -> Union[ResourceDescr, InvalidDescr]:
    opened = open_bioimageio_yaml(source)

    return build_description(
        opened.content,
        context=ValidationContext(
            root=opened.original_root, file_name=opened.original_file_name
        ),
        format_version=format_version,
    )


def save_bioimageio_yaml_only(
    rd: Union[ResourceDescr, BioimageioYamlContent, InvalidDescr],
    /,
    file: Union[NewPath, FilePath, TextIO],
):
    if isinstance(rd, ResourceDescrBase):
        content = dump_description(rd)
    else:
        content = rd

    write_yaml(cast(YamlValue, content), file)


def load_description_and_validate_format_only(
    source: PermissiveFileSource,
    /,
    *,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
) -> ValidationSummary:
    rd = load_description(source, format_version=format_version)
    assert rd.validation_summary is not None
    return rd.validation_summary
