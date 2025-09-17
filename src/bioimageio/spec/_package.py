import collections.abc
import shutil
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile, mkdtemp
from typing import IO, Dict, Literal, Optional, Sequence, Union
from zipfile import ZIP_DEFLATED

from loguru import logger
from pydantic import DirectoryPath, FilePath, NewPath

from ._description import InvalidDescr, ResourceDescr, build_description
from ._internal.common_nodes import ResourceDescrBase
from ._internal.io import (
    BioimageioYamlContent,
    BioimageioYamlSource,
    FileDescr,
    RelativeFilePath,
    ensure_is_valid_bioimageio_yaml_name,
)
from ._internal.io_basics import (
    BIOIMAGEIO_YAML,
    AbsoluteFilePath,
    BytesReader,
    FileName,
    ZipPath,
)
from ._internal.io_utils import open_bioimageio_yaml, write_yaml, write_zip
from ._internal.packaging_context import PackagingContext
from ._internal.url import HttpUrl
from ._internal.utils import get_os_friendly_file_name
from ._internal.validation_context import get_validation_context
from ._internal.warning_levels import ERROR
from ._io import load_description
from .model.v0_4 import WeightsFormat


# TODO: deprecate in favor of get_package_content
def get_resource_package_content(
    rd: ResourceDescr,
    /,
    *,
    bioimageio_yaml_file_name: FileName = BIOIMAGEIO_YAML,
    weights_priority_order: Optional[Sequence[WeightsFormat]] = None,  # model only
) -> Dict[FileName, Union[HttpUrl, AbsoluteFilePath, BioimageioYamlContent, ZipPath]]:
    ret: Dict[
        FileName, Union[HttpUrl, AbsoluteFilePath, BioimageioYamlContent, ZipPath]
    ] = {}
    for k, v in get_package_content(
        rd,
        bioimageio_yaml_file_name=bioimageio_yaml_file_name,
        weights_priority_order=weights_priority_order,
    ).items():
        if isinstance(v, FileDescr):
            if isinstance(v.source, (Path, RelativeFilePath)):
                ret[k] = v.source.absolute()
            else:
                ret[k] = v.source

        else:
            ret[k] = v

    return ret


def get_package_content(
    rd: ResourceDescr,
    /,
    *,
    bioimageio_yaml_file_name: FileName = BIOIMAGEIO_YAML,
    weights_priority_order: Optional[Sequence[WeightsFormat]] = None,  # model only
) -> Dict[FileName, Union[FileDescr, BioimageioYamlContent]]:
    """
    Args:
        rd: resource description
        bioimageio_yaml_file_name: RDF file name
        # for model resources only:
        weights_priority_order: If given, only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found a ValueError is raised.
    """
    os_friendly_name = get_os_friendly_file_name(rd.name)
    bioimageio_yaml_file_name = bioimageio_yaml_file_name.format(
        name=os_friendly_name, type=rd.type
    )

    bioimageio_yaml_file_name = ensure_is_valid_bioimageio_yaml_name(
        bioimageio_yaml_file_name
    )
    content: Dict[FileName, FileDescr] = {}
    with PackagingContext(
        bioimageio_yaml_file_name=bioimageio_yaml_file_name,
        file_sources=content,
        weights_priority_order=weights_priority_order,
    ):
        rdf_content: BioimageioYamlContent = rd.model_dump(
            mode="json", exclude_unset=True
        )

    _ = rdf_content.pop("rdf_source", None)

    return {**content, bioimageio_yaml_file_name: rdf_content}


def _prepare_resource_package(
    source: Union[BioimageioYamlSource, ResourceDescr],
    /,
    *,
    weights_priority_order: Optional[Sequence[WeightsFormat]] = None,
) -> Dict[FileName, Union[BioimageioYamlContent, BytesReader]]:
    """Prepare to package a resource description; downloads all required files.

    Args:
        source: A bioimage.io resource description (as file, raw YAML content or description class)
        context: validation context
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.
    """
    context = get_validation_context()
    bioimageio_yaml_file_name = context.file_name
    if isinstance(source, ResourceDescrBase):
        descr = source
    elif isinstance(source, collections.abc.Mapping):
        descr = build_description(source)
    else:
        opened = open_bioimageio_yaml(source)
        bioimageio_yaml_file_name = opened.original_file_name
        context = context.replace(
            root=opened.original_root, file_name=opened.original_file_name
        )
        with context:
            descr = build_description(opened.content)

    if isinstance(descr, InvalidDescr):
        raise ValueError(f"{source} is invalid: {descr.validation_summary}")

    with context:
        package_content = get_package_content(
            descr,
            bioimageio_yaml_file_name=bioimageio_yaml_file_name or BIOIMAGEIO_YAML,
            weights_priority_order=weights_priority_order,
        )

    return {
        k: v if isinstance(v, collections.abc.Mapping) else v.get_reader()
        for k, v in package_content.items()
    }


def save_bioimageio_package_as_folder(
    source: Union[BioimageioYamlSource, ResourceDescr],
    /,
    *,
    output_path: Union[NewPath, DirectoryPath, None] = None,
    weights_priority_order: Optional[  # model only
        Sequence[
            Literal[
                "keras_hdf5",
                "onnx",
                "pytorch_state_dict",
                "tensorflow_js",
                "tensorflow_saved_model_bundle",
                "torchscript",
            ]
        ]
    ] = None,
) -> DirectoryPath:
    """Write the content of a bioimage.io resource package to a folder.

    Args:
        source: bioimageio resource description
        output_path: file path to write package to
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.

    Returns:
        directory path to bioimageio package folder
    """
    package_content = _prepare_resource_package(
        source,
        weights_priority_order=weights_priority_order,
    )
    if output_path is None:
        output_path = Path(mkdtemp())
    else:
        output_path = Path(output_path)

    output_path.mkdir(exist_ok=True, parents=True)
    for name, src in package_content.items():
        if isinstance(src, collections.abc.Mapping):
            write_yaml(src, output_path / name)
        elif (
            isinstance(src.original_root, Path)
            and src.original_root / src.original_file_name
            == (output_path / name).resolve()
        ):
            logger.debug(
                f"Not copying {src.original_root / src.original_file_name} to itself."
            )
        else:
            if isinstance(src.original_root, Path):
                logger.debug(
                    f"Copying from path {src.original_root / src.original_file_name} to {output_path / name}."
                )
            else:
                logger.debug(
                    f"Copying {src.original_root}/{src.original_file_name} to {output_path / name}."
                )
            with (output_path / name).open("wb") as dest:
                _ = shutil.copyfileobj(src, dest)

    return output_path


def save_bioimageio_package(
    source: Union[BioimageioYamlSource, ResourceDescr],
    /,
    *,
    compression: int = ZIP_DEFLATED,
    compression_level: int = 1,
    output_path: Union[NewPath, FilePath, None] = None,
    weights_priority_order: Optional[  # model only
        Sequence[
            Literal[
                "keras_hdf5",
                "onnx",
                "pytorch_state_dict",
                "tensorflow_js",
                "tensorflow_saved_model_bundle",
                "torchscript",
            ]
        ]
    ] = None,
    allow_invalid: bool = False,
) -> FilePath:
    """Package a bioimageio resource as a zip file.

    Args:
        rd: bioimageio resource description
        compression: The numeric constant of compression method.
        compression_level: Compression level to use when writing files to the archive.
                           See https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile
        output_path: file path to write package to
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.

    Returns:
        path to zipped bioimageio package
    """
    package_content = _prepare_resource_package(
        source,
        weights_priority_order=weights_priority_order,
    )
    if output_path is None:
        output_path = Path(
            NamedTemporaryFile(suffix=".bioimageio.zip", delete=False).name
        )
    else:
        output_path = Path(output_path)

    write_zip(
        output_path,
        package_content,
        compression=compression,
        compression_level=compression_level,
    )
    with get_validation_context().replace(warning_level=ERROR):
        if isinstance((exported := load_description(output_path)), InvalidDescr):
            exported.validation_summary.display()
            msg = f"Exported package at '{output_path}' is invalid."
            if allow_invalid:
                logger.error(msg)
            else:
                raise ValueError(msg)

    return output_path


def save_bioimageio_package_to_stream(
    source: Union[BioimageioYamlSource, ResourceDescr],
    /,
    *,
    compression: int = ZIP_DEFLATED,
    compression_level: int = 1,
    output_stream: Union[IO[bytes], None] = None,
    weights_priority_order: Optional[  # model only
        Sequence[
            Literal[
                "keras_hdf5",
                "onnx",
                "pytorch_state_dict",
                "tensorflow_js",
                "tensorflow_saved_model_bundle",
                "torchscript",
            ]
        ]
    ] = None,
) -> IO[bytes]:
    """Package a bioimageio resource into a stream.

    Args:
        rd: bioimageio resource description
        compression: The numeric constant of compression method.
        compression_level: Compression level to use when writing files to the archive.
                           See https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile
        output_stream: stream to write package to
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.

    Note: this function bypasses safety checks and does not load/validate the model after writing.

    Returns:
        stream of zipped bioimageio package
    """
    if output_stream is None:
        output_stream = BytesIO()

    package_content = _prepare_resource_package(
        source,
        weights_priority_order=weights_priority_order,
    )

    write_zip(
        output_stream,
        package_content,
        compression=compression,
        compression_level=compression_level,
    )

    return output_stream
