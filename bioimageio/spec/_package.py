import collections.abc
import re
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile, mkdtemp
from typing import Dict, Literal, Optional, Sequence, Union, cast
from zipfile import ZIP_DEFLATED

from pydantic import DirectoryPath, FilePath, NewPath

from bioimageio.spec import load_description, model
from bioimageio.spec._description import (
    InvalidDescr,
    ResourceDescr,
    build_description,
)
from bioimageio.spec._internal.base_nodes import ResourceDescrBase
from bioimageio.spec._internal.constants import BIOIMAGEIO_YAML
from bioimageio.spec._internal.io_utils import (
    download,
    open_bioimageio_yaml,
    write_yaml,
    write_zip,
)
from bioimageio.spec._internal.packaging_context import PackagingContext
from bioimageio.spec._internal.types import (
    AbsoluteFilePath,
    BioimageioYamlContent,
    BioimageioYamlSource,
    FileName,
    HttpUrl,
    YamlValue,
)
from bioimageio.spec._internal.types._file_source import is_valid_rdf_name
from bioimageio.spec._internal.validation_context import validation_context_var
from bioimageio.spec.model.v0_4 import WeightsFormat


def get_os_friendly_file_name(name: str) -> str:
    return re.sub(r"\W+|^(?=\d)", "_", name)


def get_resource_package_content(
    rd: ResourceDescr,
    /,
    *,
    bioimageio_yaml_file_name: FileName = BIOIMAGEIO_YAML,
    weights_priority_order: Optional[Sequence[WeightsFormat]] = None,  # model only
) -> Dict[FileName, Union[HttpUrl, AbsoluteFilePath, BioimageioYamlContent]]:
    """
    Args:
        rd: resource description
        bioimageio_yaml_file_name: RDF file name
        # for model resources only:
        weights_priority_order: If given, only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found a ValueError is raised.
    """
    if not is_valid_rdf_name(bioimageio_yaml_file_name):
        raise ValueError(
            f"Invalid file name '{bioimageio_yaml_file_name}'. Must be"
            f" '{BIOIMAGEIO_YAML}' or end with '.{BIOIMAGEIO_YAML}'"
        )

    os_friendly_name = get_os_friendly_file_name(rd.name)
    bioimageio_yaml_file_name = (
        f"{bioimageio_yaml_file_name.format(name=os_friendly_name, type=rd.type)}"
    )

    content: Dict[FileName, Union[HttpUrl, AbsoluteFilePath]] = {
        # add bioimageio.yaml file already here to avoid file name conflicts
        bioimageio_yaml_file_name: "http://placeholder.com",
    }
    with PackagingContext(file_sources=content):
        rdf_content: BioimageioYamlContent = rd.model_dump(
            mode="json", exclude_unset=True
        )

    _ = rdf_content.pop("rdf_source", None)

    if weights_priority_order is not None and isinstance(
        rd, (model.v0_4.ModelDescr, model.v0_5.ModelDescr)
    ):
        # select single weights entry
        assert isinstance(rdf_content["weights"], dict), type(rdf_content["weights"])
        for wf in weights_priority_order:
            w = rdf_content["weights"].get(wf)
            if w is not None:
                break
        else:
            raise ValueError(
                "None of the weight formats in `weights_priority_order` is present in"
                " the given model."
            )

        rdf_content["weights"] = {wf: w}
        rd_slim = build_description(rdf_content)
        assert not isinstance(
            rd_slim, InvalidDescr
        ), rd_slim.validation_summary.format()
        # repackage without other weights entries
        return get_resource_package_content(
            rd_slim, bioimageio_yaml_file_name=bioimageio_yaml_file_name
        )

    return {**content, bioimageio_yaml_file_name: rdf_content}


def _prepare_resource_package(
    source: Union[BioimageioYamlSource, ResourceDescr],
    /,
    *,
    weights_priority_order: Optional[Sequence[WeightsFormat]] = None,
) -> Dict[FileName, Union[FilePath, BioimageioYamlContent]]:
    """Prepare to package a resource description; downloads all required files.

    Args:
        source: A bioimage.io resource description (as file, raw YAML content or description class)
        context: validation context
        weights_priority_order: If given only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found all are included.
    """
    context = validation_context_var.get()
    bioimageio_yaml_file_name = context.file_name
    if isinstance(source, ResourceDescrBase):
        descr = source
    elif isinstance(source, dict):
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
        package_content = get_resource_package_content(
            descr,
            bioimageio_yaml_file_name=bioimageio_yaml_file_name,
            weights_priority_order=weights_priority_order,
        )

    local_package_content: Dict[FileName, Union[FilePath, BioimageioYamlContent]] = {}
    for k, v in package_content.items():
        if not isinstance(v, collections.abc.Mapping):
            v = download(v).path

        local_package_content[k] = v

    return local_package_content


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
    for name, source in package_content.items():
        if isinstance(source, collections.abc.Mapping):
            write_yaml(cast(YamlValue, source), output_path / name)
        else:
            shutil.copy(source, output_path / name)

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
    if isinstance((exported := load_description(output_path)), InvalidDescr):
        raise ValueError(
            f"Exported package '{output_path}' is invalid:"
            f" {exported.validation_summary}"
        )

    return output_path
