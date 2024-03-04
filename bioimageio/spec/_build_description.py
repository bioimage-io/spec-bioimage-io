from typing import Any, Callable, Mapping, Optional, Type, TypeVar, Union

from ._internal.common_nodes import InvalidDescr, ResourceDescrBase
from ._internal.io import BioimageioYamlContent
from ._internal.types import FormatVersionPlaceholder
from ._internal.validation_context import ValidationContext, validation_context_var
from .generic import GenericDescr

ResourceDescrT = TypeVar("ResourceDescrT", bound=ResourceDescrBase)


DISCOVER: FormatVersionPlaceholder = "discover"
"""placeholder for whatever format version an RDF specifies"""


def get_rd_class_impl(
    typ: Any,
    format_version: Any,
    descriptions_map: Mapping[
        Optional[str], Mapping[Optional[str], Type[ResourceDescrT]]
    ],
) -> Type[ResourceDescrT]:
    assert None in descriptions_map
    assert all(None in version_map for version_map in descriptions_map.values())
    assert all(
        fv is None or fv.count(".") == 1
        for version_map in descriptions_map.values()
        for fv in version_map
    )
    if not isinstance(typ, str) or typ not in descriptions_map:
        typ = None

    if (ndots := format_version.count(".")) == 0:
        use_format_version = format_version + ".0"
    elif ndots == 2:
        use_format_version = format_version[: format_version.rfind(".")]
    else:
        use_format_version = None

    descr_versions = descriptions_map[typ]
    return descr_versions.get(use_format_version, descr_versions[None])


def build_description_impl(
    content: BioimageioYamlContent,
    /,
    *,
    context: Optional[ValidationContext] = None,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
    get_rd_class: Callable[[Any, Any], Type[ResourceDescrT]],
) -> Union[ResourceDescrT, InvalidDescr]:
    context = context or validation_context_var.get()
    if not isinstance(content, dict):
        # "Invalid content of type '{type(content)}'"
        rd_class = GenericDescr

    typ = content.get("type")
    rd_class = get_rd_class(typ, content.get("format_version"))

    rd = rd_class.load(content, context=context)
    assert rd.validation_summary is not None
    if format_version != DISCOVER and not isinstance(rd, InvalidDescr):
        discover_details = rd.validation_summary.details
        as_rd_class = get_rd_class(typ, format_version)
        rd = as_rd_class.load(content, context=context)
        assert rd.validation_summary is not None
        rd.validation_summary.details[:0] = discover_details

    return rd
