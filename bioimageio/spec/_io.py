from typing import Dict, Literal, Optional, TextIO, Union, cast
from zipfile import ZipFile

from loguru import logger
from pydantic import FilePath, NewPath

from ._description import (
    DISCOVER,
    InvalidDescr,
    ResourceDescr,
    build_description,
    dump_description,
    ensure_description_is_dataset,
    ensure_description_is_model,
)
from ._internal._settings import settings
from ._internal.common_nodes import ResourceDescrBase
from ._internal.io import BioimageioYamlContent, YamlValue
from ._internal.io_basics import Sha256
from ._internal.io_utils import open_bioimageio_yaml, write_yaml
from ._internal.validation_context import validation_context_var
from .common import PermissiveFileSource
from .dataset import AnyDatasetDescr
from .model import AnyModelDescr
from .summary import ValidationSummary


def load_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
    perform_io_checks: bool = settings.perform_io_checks,
    known_files: Optional[Dict[str, Sha256]] = None,
) -> Union[ResourceDescr, InvalidDescr]:
    """load a bioimage.io resource description

    Args:
        source: Path or URL to an rdf.yaml or a bioimage.io package
                (zip-file with rdf.yaml in it).
        format_version: (optional) Use this argument to load the resource and
                        convert its metadata to a higher format_version.
        perform_io_checks: Wether or not to perform validation that requires file io,
                           e.g. downloading a remote files. The existence of local
                           absolute file paths is still being checked.
        known_files: Allows to bypass download and hashing of referenced files
                     (even if perform_io_checks is True).

    Returns:
        An object holding all metadata of the bioimage.io resource

    """
    if isinstance(source, ResourceDescrBase):
        name = getattr(source, "name", f"{str(source)[:10]}...")
        logger.warning("returning already loaded description '{}' as is", name)
        return source  # pyright: ignore[reportReturnType]

    opened = open_bioimageio_yaml(source)

    context = validation_context_var.get().replace(
        root=opened.original_root,
        file_name=opened.original_file_name,
        perform_io_checks=perform_io_checks,
        known_files=known_files,
    )

    return build_description(
        opened.content,
        context=context,
        format_version=format_version,
    )


def load_model_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
    perform_io_checks: bool = settings.perform_io_checks,
    known_files: Optional[Dict[str, Sha256]] = None,
) -> AnyModelDescr:
    """same as `load_description`, but addtionally ensures that the loaded
    description is valid and of type 'model'.

    Raises:
        ValueError: for invalid or non-model resources
    """
    rd = load_description(
        source,
        format_version=format_version,
        perform_io_checks=perform_io_checks,
        known_files=known_files,
    )
    return ensure_description_is_model(rd)


def load_dataset_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
    perform_io_checks: bool = settings.perform_io_checks,
    known_files: Optional[Dict[str, Sha256]] = None,
) -> AnyDatasetDescr:
    """same as `load_description`, but addtionally ensures that the loaded
    description is valid and of type 'dataset'.
    """
    rd = load_description(
        source,
        format_version=format_version,
        perform_io_checks=perform_io_checks,
        known_files=known_files,
    )
    return ensure_description_is_dataset(rd)


def save_bioimageio_yaml_only(
    rd: Union[ResourceDescr, BioimageioYamlContent, InvalidDescr],
    /,
    file: Union[NewPath, FilePath, TextIO],
):
    """write the metadata of a resource description (`rd`) to `file`
    without writing any of the referenced files in it.

    Note: To save a resource description with its associated files as a package,
    use `save_bioimageio_package` or `save_bioimageio_package_as_folder`.
    """
    if isinstance(rd, ResourceDescrBase):
        content = dump_description(rd)
    else:
        content = rd

    write_yaml(cast(YamlValue, content), file)


def load_description_and_validate_format_only(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
    perform_io_checks: bool = settings.perform_io_checks,
    known_files: Optional[Dict[str, Sha256]] = None,
) -> ValidationSummary:
    """load a bioimage.io resource description

    Args:
        source: Path or URL to an rdf.yaml or a bioimage.io package
                (zip-file with rdf.yaml in it).
        format_version: (optional) Use this argument to load the resource and
                        convert its metadata to a higher format_version.
        perform_io_checks: Wether or not to perform validation that requires file io,
                           e.g. downloading a remote files. The existence of local
                           absolute file paths is still being checked.
        known_files: Allows to bypass download and hashing of referenced files
                     (even if perform_io_checks is True).

    Returns:
        Validation summary of the bioimage.io resource found at `source`.

    """
    rd = load_description(
        source,
        format_version=format_version,
        perform_io_checks=perform_io_checks,
        known_files=known_files,
    )
    assert rd.validation_summary is not None
    return rd.validation_summary
