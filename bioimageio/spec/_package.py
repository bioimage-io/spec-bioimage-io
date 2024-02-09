import collections.abc
import re
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile, mkdtemp
from typing import Any, Dict, Literal, Optional, Sequence, Tuple, Union, cast
from zipfile import ZIP_DEFLATED

from pydantic import AnyUrl, DirectoryPath, FilePath, HttpUrl, NewPath

from bioimageio.spec import model
from bioimageio.spec._description import InvalidDescription, ResourceDescr, build_description, dump_description
from bioimageio.spec._internal.base_nodes import Node, ResourceDescriptionBase
from bioimageio.spec._internal.constants import BIOIMAGEIO_YAML, IN_PACKAGE_MESSAGE
from bioimageio.spec._internal.io_utils import (
    download,
    open_bioimageio_yaml,
    write_yaml,
    write_zip,
)
from bioimageio.spec._internal.types import (
    AbsoluteFilePath,
    BioimageioYamlContent,
    BioimageioYamlSource,
    FileName,
    RelativeFilePath,
    YamlValue,
)
from bioimageio.spec._internal.types._file_source import extract_file_name
from bioimageio.spec._internal.utils import nest_dict_with_narrow_first_key
from bioimageio.spec._internal.validation_context import validation_context_var
from bioimageio.spec.model.v0_4 import WeightsFormat
from bioimageio.spec.summary import Loc


def fill_resource_package_content(
    package_content: Dict[Loc, Union[HttpUrl, AbsoluteFilePath]],
    node: Node,
    node_loc: Loc,
):
    field_value: Union[Tuple[Any, ...], Node, Any]
    for field_name, field_value in node:
        loc = node_loc + (field_name,)
        # nested node
        if isinstance(field_value, Node):
            fill_resource_package_content(package_content, field_value, loc)

        # nested node in list/tuple
        elif isinstance(field_value, (list, tuple)):
            for i, fv in enumerate(field_value):
                if isinstance(fv, Node):
                    fill_resource_package_content(package_content, fv, loc + (i,))

        elif (node.model_fields[field_name].description or "").startswith(IN_PACKAGE_MESSAGE):
            if isinstance(field_value, RelativeFilePath):
                src = field_value.absolute
            elif isinstance(field_value, AnyUrl):
                src = field_value
            else:
                raise NotImplementedError(f"Package field of type {type(field_value)} not implemented.")

            package_content[loc] = src


def get_os_friendly_file_name(name: str) -> str:
    return re.sub(r"\W+|^(?=\d)", "_", name)


def get_resource_package_content(
    rd: ResourceDescr,
    /,
    *,
    bioimageio_yaml_file_name: str = BIOIMAGEIO_YAML,
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
    if bioimageio_yaml_file_name != BIOIMAGEIO_YAML and not bioimageio_yaml_file_name.endswith(
        f".{BIOIMAGEIO_YAML}"
    ):
        raise ValueError(
            f"Invalid file name '{bioimageio_yaml_file_name}'. Must be '{BIOIMAGEIO_YAML}' or end with '.{BIOIMAGEIO_YAML}'"
        )

    if weights_priority_order is not None and isinstance(rd, (model.v0_4.ModelDescr, model.v0_5.ModelDescr)):
        # select single weights entry
        for wf in weights_priority_order:
            w = getattr(rd.weights, wf, None)
            if w is not None:
                break
        else:
            raise ValueError("None of the weight formats in `weights_priority_order` is present in the given model.")

        rd = rd.model_copy(update=dict(weights={wf: w}))

    package_content: Dict[Loc, Union[HttpUrl, AbsoluteFilePath]] = {}
    fill_resource_package_content(package_content, rd, node_loc=())
    file_names: Dict[Loc, str] = {}
    os_friendly_name = get_os_friendly_file_name(rd.name)
    content: BioimageioYamlContent = {}  # filled in below
    reserved_file_sources: Dict[str, BioimageioYamlContent] = {
        "rdf.yaml": content,  # legacy name
        f"{bioimageio_yaml_file_name.format(name=os_friendly_name, type=rd.type)}": content,
    }
    file_sources: Dict[str, Union[HttpUrl, AbsoluteFilePath, BioimageioYamlContent]] = dict(reserved_file_sources)
    for loc, src in package_content.items():
        file_name = extract_file_name(src)
        if file_name in file_sources and file_sources[file_name] != src:
            for i in range(2, 10):
                fn, *ext = file_name.split(".")
                alternative_file_name = ".".join([f"{fn}_{i}", *ext])
                if alternative_file_name not in file_sources or file_sources[alternative_file_name] == src:
                    file_name = alternative_file_name
                    break
            else:
                raise RuntimeError(f"Too many file name clashes for {file_name}")

        file_sources[file_name] = src
        file_names[loc] = file_name

    # update resource description to point to local files
    rd = rd.model_copy(update=nest_dict_with_narrow_first_key(file_names, str))

    # fill in rdf content from updated resource description
    content.update(dump_description(rd))

    return file_sources


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
    if isinstance(source, ResourceDescriptionBase):
        descr = source
    elif isinstance(source, dict):
        descr = build_description(source)
    else:
        opened = open_bioimageio_yaml(source)
        outer_context = validation_context_var.get()
        with outer_context.replace(root=opened.original_root, file_name=opened.original_file_name):
            descr = build_description(opened.content)

    if isinstance(descr, InvalidDescription):
        raise ValueError(f"{source} is invalid: {descr.validation_summary}")

    package_content = get_resource_package_content(descr, weights_priority_order=weights_priority_order)

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
        output_path = Path(NamedTemporaryFile(suffix=".bioimageio.zip", delete=False).name)
    else:
        output_path = Path(output_path)

    write_zip(output_path, package_content, compression=compression, compression_level=compression_level)
    return output_path
