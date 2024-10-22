"""implementation details for building a bioimage.io resource description"""

from typing import Any, Callable, List, Mapping, Optional, Type, TypeVar, Union

from ._internal.common_nodes import InvalidDescr, ResourceDescrBase
from ._internal.io import BioimageioYamlContent
from ._internal.types import FormatVersionPlaceholder
from ._internal.validation_context import ValidationContext, validation_context_var
from .summary import (
    WARNING_LEVEL_TO_NAME,
    ErrorEntry,
    ValidationContextSummary,
    ValidationDetail,
)

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
    errors: List[ErrorEntry] = []
    if isinstance(content, dict):
        for minimum in ("type", "format_version"):
            if minimum not in content:
                errors.append(
                    ErrorEntry(
                        loc=(minimum,), msg=f"Missing field '{minimum}'", type="error"
                    )
                )
            elif not isinstance(content[minimum], str):
                errors.append(
                    ErrorEntry(
                        loc=(minimum,),
                        msg=f"Invalid type '{type(content[minimum])}'",
                        type="error",
                    )
                )
    else:
        errors.append(
            ErrorEntry(
                loc=(), msg=f"Invalid content of type '{type(content)}'", type="error"
            )
        )
        content = {}

    if errors:
        ret = InvalidDescr(**content)  # pyright: ignore[reportArgumentType]
        ret.validation_summary.add_detail(
            ValidationDetail(
                name="extract fields to chose description class",
                status="failed",
                errors=errors,
                context=ValidationContextSummary(
                    perform_io_checks=context.perform_io_checks,
                    known_files=context.known_files,
                    root=str(context.root),
                    warning_level=WARNING_LEVEL_TO_NAME[context.warning_level],
                ),
            )
        )
        return ret

    typ = content["type"]
    rd_class = get_rd_class(typ, content["format_version"])
    rd = rd_class.load(content, context=context)

    if format_version != DISCOVER and not isinstance(rd, InvalidDescr):
        # load with requested format_version
        discover_details = rd.validation_summary.details
        as_rd_class = get_rd_class(typ, format_version)
        rd = as_rd_class.load(content, context=context)
        assert rd.validation_summary is not None
        rd.validation_summary.details[:0] = discover_details

    return rd
