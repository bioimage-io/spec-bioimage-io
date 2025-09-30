import collections.abc
from pathlib import Path
from typing import Dict, Literal, Optional, TextIO, Union, cast, overload
from zipfile import ZipFile

from loguru import logger
from pydantic import FilePath, NewPath

from ._description import (
    DISCOVER,
    LATEST,
    InvalidDescr,
    LatestResourceDescr,
    ResourceDescr,
    build_description,
    dump_description,
    ensure_description_is_dataset,
    ensure_description_is_model,
)
from ._internal.common_nodes import ResourceDescrBase
from ._internal.io import BioimageioYamlContent, YamlValue
from ._internal.io_basics import Sha256
from ._internal.io_utils import open_bioimageio_yaml, write_yaml
from ._internal.types import FormatVersionPlaceholder
from ._internal.validation_context import get_validation_context
from .common import PermissiveFileSource
from .dataset import AnyDatasetDescr, DatasetDescr
from .model import AnyModelDescr, ModelDescr
from .summary import ValidationSummary


@overload
def load_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Literal["latest"],
    perform_io_checks: Optional[bool] = None,
    known_files: Optional[Dict[str, Optional[Sha256]]] = None,
    sha256: Optional[Sha256] = None,
) -> Union[LatestResourceDescr, InvalidDescr]: ...


@overload
def load_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
    perform_io_checks: Optional[bool] = None,
    known_files: Optional[Dict[str, Optional[Sha256]]] = None,
    sha256: Optional[Sha256] = None,
) -> Union[ResourceDescr, InvalidDescr]: ...


def load_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
    perform_io_checks: Optional[bool] = None,
    known_files: Optional[Dict[str, Optional[Sha256]]] = None,
    sha256: Optional[Sha256] = None,
) -> Union[ResourceDescr, InvalidDescr]:
    """load a bioimage.io resource description

    Args:
        source:
            Path or URL to an rdf.yaml or a bioimage.io package
            (zip-file with rdf.yaml in it).
        format_version:
            (optional) Use this argument to load the resource and
            convert its metadata to a higher format_version.
            Note:
            - Use "latest" to convert to the latest available format version.
            - Use "discover" to use the format version specified in the RDF.
            - Only considers major.minor format version, ignores patch version.
            - Conversion to lower format versions is not supported.
        perform_io_checks:
            Wether or not to perform validation that requires file io,
            e.g. downloading a remote files. The existence of local
            absolute file paths is still being checked.
        known_files:
            Allows to bypass download and hashing of referenced files
            (even if perform_io_checks is True).
            Checked files will be added to this dictionary
            with their SHA-256 value.
        sha256:
            Optional SHA-256 value of **source**

    Returns:
        An object holding all metadata of the bioimage.io resource

    """
    if isinstance(source, ResourceDescrBase):
        name = getattr(source, "name", f"{str(source)[:10]}...")
        logger.warning("returning already loaded description '{}' as is", name)
        return source  # pyright: ignore[reportReturnType]

    opened = open_bioimageio_yaml(source, sha256=sha256)

    context = get_validation_context().replace(
        root=opened.original_root,
        file_name=opened.original_file_name,
        original_source_name=opened.original_source_name,
        perform_io_checks=perform_io_checks,
        known_files=known_files,
    )

    return build_description(
        opened.content,
        context=context,
        format_version=format_version,
    )


@overload
def load_model_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Literal["latest"],
    perform_io_checks: Optional[bool] = None,
    known_files: Optional[Dict[str, Optional[Sha256]]] = None,
    sha256: Optional[Sha256] = None,
) -> ModelDescr: ...


@overload
def load_model_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
    perform_io_checks: Optional[bool] = None,
    known_files: Optional[Dict[str, Optional[Sha256]]] = None,
    sha256: Optional[Sha256] = None,
) -> AnyModelDescr: ...


def load_model_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
    perform_io_checks: Optional[bool] = None,
    known_files: Optional[Dict[str, Optional[Sha256]]] = None,
    sha256: Optional[Sha256] = None,
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
        sha256=sha256,
    )
    return ensure_description_is_model(rd)


@overload
def load_dataset_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Literal["latest"],
    perform_io_checks: Optional[bool] = None,
    known_files: Optional[Dict[str, Optional[Sha256]]] = None,
    sha256: Optional[Sha256] = None,
) -> DatasetDescr: ...


@overload
def load_dataset_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
    perform_io_checks: Optional[bool] = None,
    known_files: Optional[Dict[str, Optional[Sha256]]] = None,
    sha256: Optional[Sha256] = None,
) -> AnyDatasetDescr: ...


def load_dataset_description(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
    perform_io_checks: Optional[bool] = None,
    known_files: Optional[Dict[str, Optional[Sha256]]] = None,
    sha256: Optional[Sha256] = None,
) -> AnyDatasetDescr:
    """same as `load_description`, but addtionally ensures that the loaded
    description is valid and of type 'dataset'.
    """
    rd = load_description(
        source,
        format_version=format_version,
        perform_io_checks=perform_io_checks,
        known_files=known_files,
        sha256=sha256,
    )
    return ensure_description_is_dataset(rd)


def save_bioimageio_yaml_only(
    rd: Union[ResourceDescr, BioimageioYamlContent, InvalidDescr],
    /,
    file: Union[NewPath, FilePath, TextIO],
    *,
    exclude_unset: bool = True,
    exclude_defaults: bool = False,
):
    """write the metadata of a resource description (`rd`) to `file`
    without writing any of the referenced files in it.

    Args:
        rd: bioimageio resource description
        file: file or stream to save to
        exclude_unset: Exclude fields that have not explicitly be set.
        exclude_defaults: Exclude fields that have the default value (even if set explicitly).

    Note: To save a resource description with its associated files as a package,
    use `save_bioimageio_package` or `save_bioimageio_package_as_folder`.
    """
    if isinstance(rd, ResourceDescrBase):
        content = dump_description(
            rd, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults
        )
    else:
        content = rd

    write_yaml(cast(YamlValue, content), file)


def load_description_and_validate_format_only(
    source: Union[PermissiveFileSource, ZipFile],
    /,
    *,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
    perform_io_checks: Optional[bool] = None,
    known_files: Optional[Dict[str, Optional[Sha256]]] = None,
    sha256: Optional[Sha256] = None,
) -> ValidationSummary:
    """same as `load_description`, but only return the validation summary.

    Returns:
        Validation summary of the bioimage.io resource found at `source`.

    """
    rd = load_description(
        source,
        format_version=format_version,
        perform_io_checks=perform_io_checks,
        known_files=known_files,
        sha256=sha256,
    )
    assert rd.validation_summary is not None
    return rd.validation_summary


def update_format(
    source: Union[
        ResourceDescr,
        PermissiveFileSource,
        ZipFile,
        BioimageioYamlContent,
        InvalidDescr,
    ],
    /,
    *,
    output: Union[Path, TextIO, None] = None,
    exclude_defaults: bool = True,
    perform_io_checks: Optional[bool] = None,
) -> Union[LatestResourceDescr, InvalidDescr]:
    """Update a resource description.

    Notes:
    - Invalid **source** descriptions may fail to update.
    - The updated description might be invalid (even if the **source** was valid).
    """

    if isinstance(source, ResourceDescrBase):
        root = source.root
        source = dump_description(source)
    else:
        root = None

    if isinstance(source, collections.abc.Mapping):
        descr = build_description(
            source,
            context=get_validation_context().replace(
                root=root, perform_io_checks=perform_io_checks
            ),
            format_version=LATEST,
        )

    else:
        descr = load_description(
            source,
            perform_io_checks=perform_io_checks,
            format_version=LATEST,
        )

    if output is not None:
        save_bioimageio_yaml_only(descr, file=output, exclude_defaults=exclude_defaults)

    return descr


def update_hashes(
    source: Union[PermissiveFileSource, ZipFile, ResourceDescr, BioimageioYamlContent],
    /,
) -> Union[ResourceDescr, InvalidDescr]:
    """Update hash values of the files referenced in **source**."""
    if isinstance(source, ResourceDescrBase):
        root = source.root
        source = dump_description(source)
    else:
        root = None

    context = get_validation_context().replace(
        update_hashes=True, root=root, perform_io_checks=True
    )
    with context:
        if isinstance(source, collections.abc.Mapping):
            return build_description(source)
        else:
            return load_description(source, perform_io_checks=True)
