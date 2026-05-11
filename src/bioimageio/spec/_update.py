import collections.abc
import warnings
from pathlib import Path
from typing import Optional, TextIO, Union
from zipfile import ZipFile

from ._description import (
    LATEST,
    InvalidDescr,
    LatestResourceDescr,
    ResourceDescr,
    build_description,
    dump_description,
)
from ._internal.common_nodes import ResourceDescrBase
from ._internal.io import BioimageioYamlContent
from ._internal.types import PermissiveFileSource
from ._internal.validation_context import get_validation_context
from ._io import load_description, save_bioimageio_yaml_only
from ._package import save_bioimageio_package, save_bioimageio_package_as_folder


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

    if output is None:
        pass
    elif isinstance(output, (str, Path)):
        output = Path(output)
        if output.suffix in {".yaml", ".yml"}:
            save_bioimageio_yaml_only(
                descr, file=output, exclude_defaults=exclude_defaults
            )
        elif isinstance(descr, InvalidDescr):
            output = output.with_name(output.stem + "_invalid.yaml")
            warnings.warn(
                f"description is invalid, saving bioimageio.yaml to '{output}'"
            )
            save_bioimageio_yaml_only(
                descr, file=output, exclude_defaults=exclude_defaults
            )
        elif not output.suffix:
            _ = save_bioimageio_package_as_folder(descr, output_path=output)
        else:
            _ = save_bioimageio_package(descr, output_path=output)
    else:
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
