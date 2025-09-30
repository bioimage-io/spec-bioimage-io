"""implementation details for building a bioimage.io resource description"""

import collections.abc
from typing import Any, Callable, List, Literal, Mapping, Optional, Type, TypeVar, Union

from ._internal.common_nodes import InvalidDescr, ResourceDescrBase
from ._internal.io import BioimageioYamlContentView
from ._internal.types import FormatVersionPlaceholder
from ._internal.validation_context import ValidationContext, get_validation_context
from .summary import (
    ErrorEntry,
    ValidationDetail,
)

ResourceDescrT = TypeVar("ResourceDescrT", bound=ResourceDescrBase)


DISCOVER: Literal["discover"] = "discover"
"""placeholder for whatever format version an RDF specifies"""


def get_rd_class_impl(
    typ: Any,
    format_version: Any,
    descriptions_map: Mapping[
        Optional[str], Mapping[Optional[str], Type[ResourceDescrT]]
    ],
) -> Type[ResourceDescrT]:
    """get the resource description class for the given type and format version"""
    assert None in descriptions_map
    assert all("latest" in version_map for version_map in descriptions_map.values())
    assert all(
        fv == "latest" or fv.count(".") == 1
        for version_map in descriptions_map.values()
        for fv in version_map
    )
    if not isinstance(typ, str) or typ not in descriptions_map:
        typ = None

    format_version = str(format_version)
    if format_version == "latest" or (ndots := format_version.count(".")) == 1:
        use_format_version = format_version
    elif ndots == 0:
        use_format_version = format_version + ".0"
    else:
        assert ndots > 1
        use_format_version = format_version[: format_version.rfind(".")]

    descr_versions = descriptions_map[typ]
    if use_format_version not in descr_versions:
        raise ValueError(
            f"Unsupported format version '{format_version}' for type '{typ}'. "
            f"Supported format versions are: {', '.join(sorted(fv for fv in descr_versions if fv is not None))}"
        )

    return descr_versions[use_format_version]


def build_description_impl(
    content: BioimageioYamlContentView,
    /,
    *,
    context: Optional[ValidationContext] = None,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
    get_rd_class: Callable[[Any, Any], Type[ResourceDescrT]],
) -> Union[ResourceDescrT, InvalidDescr]:
    context = context or get_validation_context()
    errors: List[ErrorEntry] = []
    if isinstance(content, collections.abc.Mapping):
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
                context=context.summary,
            )
        )
        return ret

    typ = content["type"]
    rd_class = get_rd_class(typ, content["format_version"])
    rd = rd_class.load(content, context=context)

    if str(format_version).lower() not in (
        DISCOVER,
        rd_class.implemented_format_version,
        ".".join(map(str, rd_class.implemented_format_version_tuple[:2])),
    ):
        # load with requested format_version
        discover_details = rd.validation_summary.details
        as_rd_class = get_rd_class(typ, format_version)
        rd = as_rd_class.load(content, context=context)
        assert rd.validation_summary is not None
        rd.validation_summary.details[:0] = discover_details

    return rd
