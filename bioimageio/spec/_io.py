from typing import Literal, TextIO, Union, cast

from loguru import logger
from pydantic import FilePath, NewPath

from ._description import (
    DISCOVER,
    InvalidDescr,
    ResourceDescr,
    build_description,
    dump_description,
)
from ._internal._settings import settings
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
    perform_io_checks: bool = settings.perform_io_checks,
) -> Union[ResourceDescr, InvalidDescr]:
    """load a bioimage.io resource description

    Args:
        source: Path or URL to an rdf.yaml or a bioimage.io package
                (zip-file with rdf.yaml in it)
        format_version: (optional) use this argument to load the resource and
                        convert its metadata to a higher format_version
        perform_io_checks: wether or not to perform validation that requires file io,
                           e.g. downloading a remote files. The existence of local
                           absolute file paths is still being checked.

    Returns:
        An object holding all metadata of the bioimage.io resource

    """
    if isinstance(source, ResourceDescrBase):
        name = getattr(source, "name", f"{str(source)[:10]}...")
        logger.warning("returning already loaded description '{}' as is", name)
        return source  # pyright: ignore[reportReturnType]

    opened = open_bioimageio_yaml(source)

    return build_description(
        opened.content,
        context=ValidationContext(
            root=opened.original_root,
            file_name=opened.original_file_name,
            perform_io_checks=perform_io_checks,
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
