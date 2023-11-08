import re
from typing import Any, Dict, Optional, Sequence, Tuple, Union

from pydantic import AnyUrl, HttpUrl

from bioimageio.spec import model
from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.constants import IN_PACKAGE_MESSAGE
from bioimageio.spec._internal.utils import extract_file_name, nest_dict_with_narrow_first_key
from bioimageio.spec.description import ResourceDescription, dump_description
from bioimageio.spec.summary import Loc
from bioimageio.spec.typing import FileName, RdfContent, RelativeFilePath


def _fill_resource_package_content(
    package_content: Dict[Loc, Union[HttpUrl, RelativeFilePath]],
    node: Node,
    node_loc: Loc,
):
    field_value: Union[Tuple[Any, ...], Node, Any]
    for field_name, field_value in node:
        loc = node_loc + (field_name,)
        # nested node
        if isinstance(field_value, Node):
            _fill_resource_package_content(package_content, field_value, loc)

        # nested node in tuple
        elif isinstance(field_value, tuple):
            for i, fv in enumerate(field_value):
                if isinstance(fv, Node):
                    _fill_resource_package_content(package_content, fv, loc + (i,))

        elif (node.model_fields[field_name].description or "").startswith(IN_PACKAGE_MESSAGE):
            if isinstance(field_value, RelativeFilePath):
                src = field_value
            elif isinstance(field_value, AnyUrl):
                src = field_value
            else:
                raise NotImplementedError(f"Package field of type {type(field_value)} not implemented.")

            package_content[loc] = src


def _get_os_friendly_file_name(name: str) -> str:
    return re.sub(r"\W+|^(?=\d)", "_", name)


WeightsFormat = model.v0_4.WeightsFormat


def get_resource_package_content(
    rd: ResourceDescription,
    *,
    rdf_file_name: str = "{name}.{type}.bioimageio.yaml",
    weights_priority_order: Optional[Sequence[WeightsFormat]] = None,  # model only
) -> Dict[FileName, Union[HttpUrl, RelativeFilePath, RdfContent]]:
    """
    Args:
        rd: resource description
        rdf_file_name: RDF file name
        # for model resources only:
        weights_priority_order: If given, only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found a ValueError is raised.
    """
    if weights_priority_order is not None and isinstance(rd, (model.v0_4.Model, model.v0_5.Model)):
        # select single weights entry
        for wf in weights_priority_order:
            w = getattr(rd.weights, wf, None)
            if w is not None:
                break
        else:
            raise ValueError("None of the weight formats in `weights_priority_order` is present in the given model.")

        rd = rd.model_copy(update=dict(weights={wf: w}))

    package_content: Dict[Loc, Union[HttpUrl, RelativeFilePath]] = {}
    _fill_resource_package_content(package_content, rd, node_loc=())
    file_names: Dict[Loc, str] = {}
    os_friendly_name = _get_os_friendly_file_name(rd.name)
    rdf_content = {}  # filled in below
    reserved_file_sources: Dict[str, RdfContent] = {
        "rdf.yaml": rdf_content,  # legacy name
        f"{rdf_file_name.format(name=os_friendly_name, type=rd.type)}.bioimageio.yaml": rdf_content,
    }
    file_sources: Dict[str, Union[HttpUrl, RelativeFilePath, RdfContent]] = dict(reserved_file_sources)
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
    rdf_content.update(dump_description(rd))

    return file_sources
