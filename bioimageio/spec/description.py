import traceback
from copy import deepcopy
from pathlib import PurePath
from types import MappingProxyType
from typing import Any, Dict, Iterable, List, Literal, Mapping, Optional, Tuple, Type, TypeVar, Union, get_args
from urllib.parse import urljoin

import pydantic
from pydantic import Field
from pydantic_core import PydanticUndefined
from typing_extensions import Annotated

import bioimageio.spec
from bioimageio.spec import application, collection, dataset, generic, model, notebook
from bioimageio.spec._internal.base_nodes import ResourceDescriptionBase
from bioimageio.spec._internal.constants import DISCOVER, ERROR, LATEST, VERSION, WARNING_LEVEL_CONTEXT_KEY
from bioimageio.spec._internal.field_validation import ValContext, get_validation_context
from bioimageio.spec._internal.utils import nest_dict_with_narrow_first_key
from bioimageio.spec.types import (
    LegacyValidationSummary,
    RawStringDict,
    RawStringMapping,
    ValidationContext,
    ValidationError,
    ValidationSummary,
    ValidationWarning,
    WarningLevelName,
)

_ResourceDescription_v0_2 = Union[
    Annotated[
        Union[
            application.v0_2.Application,
            collection.v0_2.Collection,
            dataset.v0_2.Dataset,
            model.v0_4.Model,
            notebook.v0_2.Notebook,
        ],
        Field(discriminator="type"),
    ],
    generic.v0_2.Generic,
]
"""A resource description following the 0.2.x (model: 0.4.x) specification format"""

_ResourceDescription_v0_3 = Union[
    Annotated[
        Union[
            application.v0_3.Application,
            collection.v0_3.Collection,
            dataset.v0_3.Dataset,
            model.v0_5.Model,
            notebook.v0_3.Notebook,
        ],
        Field(discriminator="type"),
    ],
    generic.v0_3.Generic,
]
"""A resource description following the 0.3.x (model: 0.5.x) specification format"""

LatestResourceDescription = _ResourceDescription_v0_3
"""A resource description following the latest specification format"""


SpecificResourceDescription = Annotated[
    Union[
        application.AnyApplication,
        collection.AnyCollection,
        dataset.AnyDataset,
        model.AnyModel,
        notebook.AnyNotebook,
    ],
    Field(discriminator="type"),
]
"""Any of the implemented, non-generic resource descriptions"""

ResourceDescription = Union[
    SpecificResourceDescription,
    generic.AnyGeneric,
]
"""Any of the implemented resource descriptions"""


def _get_supported_format_versions() -> Mapping[str, Tuple[str, ...]]:
    supported: Dict[str, List[str]] = {}
    for typ, rd_class in _iterate_over_rd_classes():
        format_versions = supported.setdefault(typ, [])
        ma, mi, pa = rd_class.implemented_format_version_tuple
        for p in range(pa + 1):
            format_versions.append(f"{ma}.{mi}.{p}")

    supported["model"].extend([f"0.3.{i}" for i in range(7)])  # model 0.3 can be converted
    return MappingProxyType({t: tuple(fv) for t, fv in supported.items()})


def _iterate_over_rd_classes() -> Iterable[Tuple[str, Type[ResourceDescription]]]:
    for rd_class in get_args(
        Union[
            get_args(application.AnyApplication)[0],  # type: ignore
            get_args(collection.AnyCollection)[0],  # type: ignore
            get_args(dataset.AnyDataset)[0],  # type: ignore
            get_args(generic.AnyGeneric)[0],  # type: ignore
            get_args(model.AnyModel)[0],  # type: ignore
            get_args(notebook.AnyNotebook)[0],  # type: ignore
        ]
    ):
        typ = rd_class.model_fields["type"].default
        if typ is PydanticUndefined:
            typ = "generic"

        assert isinstance(typ, str)
        yield typ, rd_class


def _iterate_over_latest_rd_classes() -> Iterable[Tuple[str, Type[ResourceDescription]]]:
    for rd_class in [
        application.Application,
        collection.Collection,
        dataset.Dataset,
        generic.Generic,
        model.Model,
        notebook.Notebook,
    ]:
        typ: Any = rd_class.model_fields["type"].default
        if typ is PydanticUndefined:
            typ = "generic"

        assert isinstance(typ, str)
        yield typ, rd_class


def _check_type_and_format_version(data: RawStringMapping) -> Tuple[str, str, str]:
    typ = data.get("type")
    if not isinstance(typ, str):
        raise TypeError(f"Invalid resource type '{typ}' of type {type(typ)}")

    fv = data.get("format_version")
    if not isinstance(fv, str):
        raise TypeError(f"Invalid format version '{fv}' of type {type(fv)}")

    if fv in _get_supported_format_versions().get(typ, ()):
        use_fv = fv
    elif hasattr(bioimageio.spec, typ):
        # type is specialized...
        type_module = getattr(bioimageio.spec, typ)
        # ...and major/minor format version is unknown
        v_module = type_module  # use latest
        if fv.count(".") == 2:
            v_module_name = f"v{fv[:fv.rfind('.')].replace('.', '_')}"
            if hasattr(type_module, v_module_name):
                # ...and we know the major/minor format version (only patch is unknown)
                v_module = getattr(type_module, v_module_name)

        rd_class = getattr(v_module, typ.capitalize())
        assert issubclass(rd_class, ResourceDescriptionBase)
        use_fv = rd_class.implemented_format_version
    else:
        # fallback: type is not specialized (yet) and format version is unknown
        use_fv = bioimageio.spec.generic.Generic.implemented_format_version  # latest generic

    return typ, fv, use_fv


def _get_rd_class(type_: str, /, format_version: str = LATEST) -> Union[Type[ResourceDescription], str]:
    """Get the appropriate resource description class for a given `type` and `format_version`.

    returns:
        resource description class
        or string with error message

    """
    assert isinstance(format_version, str)
    if format_version != LATEST and format_version.count(".") == 0:
        format_version = format_version + ".0"
    elif format_version.count(".") == 2:
        format_version = format_version[: format_version.rfind(".")]

    rd_classes: Dict[str, Dict[str, Type[ResourceDescription]]] = {}
    for typ, rd_class in _iterate_over_rd_classes():
        per_fv: Dict[str, Type[ResourceDescription]] = rd_classes.setdefault(typ, {})

        ma, mi, _pa = rd_class.implemented_format_version_tuple
        key = f"{ma}.{mi}"
        assert key not in per_fv
        per_fv[key] = rd_class

    for typ, rd_class in _iterate_over_latest_rd_classes():
        rd_classes[typ]["latest"] = rd_class

    rd_class = rd_classes.get(type_, rd_classes["generic"]).get(format_version)
    if rd_class is None:
        return f"{type_} (or generic) specification {format_version} does not exist."

    return rd_class


def update_format(
    rdf_content: RawStringMapping,
    update_to_format: str = "latest",
    context: Optional[ValidationContext] = None,
) -> RawStringMapping:
    """Auto-update fields of a bioimage.io resource without any validation."""
    assert "type" in rdf_content
    assert isinstance(rdf_content["type"], str)
    rd_class = _get_rd_class(rdf_content["type"], update_to_format)
    if isinstance(rd_class, str):
        raise ValueError(rd_class)

    rd = dict(rdf_content)
    val_context = get_validation_context(**(context or {}))
    rd_class.convert_from_older_format(rd, val_context)
    return rd


RD = TypeVar("RD", bound=ResourceDescriptionBase)


def dump_description(rd: ResourceDescription) -> RawStringDict:
    """Converts a resource to a dictionary containing only simple types that can directly be serialzed to YAML."""
    return rd.model_dump(mode="json", exclude={"root"})


def _load_descr_impl(rd_class: Type[RD], rdf_content: RawStringMapping, context: ValContext):
    rd: Optional[RD] = None
    val_errors: List[ValidationError] = []
    val_warnings: List[ValidationWarning] = []
    tb: Optional[List[str]] = None

    try:
        rd = rd_class.model_validate(rdf_content, context=dict(context))
    except pydantic.ValidationError as e:
        for ee in e.errors(include_url=False):
            if (type_ := ee["type"]) in get_args(WarningLevelName):
                val_warnings.append(ValidationWarning(loc=ee["loc"], msg=ee["msg"], type=type_))  # type: ignore
            else:
                val_errors.append(ValidationError(loc=ee["loc"], msg=ee["msg"], type=ee["type"]))

    except Exception as e:
        val_errors.append(ValidationError(loc=(), msg=str(e), type=type(e).__name__))
        tb = traceback.format_tb(e.__traceback__)

    return rd, val_errors, tb, val_warnings


def _load_description_with_known_rd_class(
    rdf_content: RawStringMapping,
    *,
    context: Optional[ValidationContext] = None,
    rd_class: Type[RD],
) -> Tuple[Optional[RD], ValidationSummary]:
    val_context = get_validation_context(**(context or {}))

    raw_rd = deepcopy(dict(rdf_content))
    rd, errors, tb, val_warnings = _load_descr_impl(
        rd_class,
        raw_rd,
        {**val_context, WARNING_LEVEL_CONTEXT_KEY: ERROR},
    )  # ignore any warnings using warning level 'ERROR'/'CRITICAL' on first loading attempt
    if rd is None:
        resource_type = rd_class.model_fields["type"].default
        format_version = rd_class.implemented_format_version
    else:
        resource_type = rd.type
        format_version = rd.format_version
        assert not errors, f"got rd, but also errors: {errors}"
        assert tb is None, f"got rd, but also an error traceback: {tb}"
        assert not val_warnings, f"got rd, but also already warnings: {val_warnings}"
        _, error2, tb2, val_warnings = _load_descr_impl(rd_class, raw_rd, val_context)
        assert not error2, f"increasing warning level caused errors: {error2}"
        assert tb2 is None, f"increasing warning level lead to error traceback: {tb2}"

    summary = ValidationSummary(
        bioimageio_spec_version=VERSION,
        errors=errors,
        name=f"bioimageio.spec static {resource_type} validation (format version: {format_version}).",
        source_name=(val_context["root"] / val_context["file_name"]).as_posix()
        if isinstance(val_context["root"], PurePath)
        else urljoin(str(val_context["root"]), val_context["file_name"]),
        status="failed" if errors else "passed",
        warnings=val_warnings,
    )
    if tb:
        summary["traceback"] = tb

    return rd, summary


def load_description(
    rdf_content: RawStringMapping,
    *,
    context: Optional[ValidationContext] = None,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
) -> Tuple[Optional[ResourceDescription], ValidationSummary]:
    discovered_type, discovered_format_version, use_format_version = _check_type_and_format_version(rdf_content)
    if use_format_version != discovered_format_version:
        rdf_content = dict(rdf_content)
        rdf_content["format_version"] = use_format_version
        future_patch_warning = ValidationWarning(
            loc=("format_version",),
            msg=f"Treated future patch version {discovered_format_version} as {use_format_version}.",
            type="alert",
        )
    else:
        future_patch_warning = None

    fv = use_format_version if format_version == DISCOVER else format_version
    rd_class = _get_rd_class(discovered_type, format_version=fv)
    if isinstance(rd_class, str):
        rd = None
        val_context = get_validation_context(**(context or {}))
        root = val_context["root"]
        file_name = val_context["file_name"]
        summary = ValidationSummary(
            bioimageio_spec_version=VERSION,
            errors=[ValidationError(loc=(), msg=rd_class, type="error")],
            name=f"bioimageio.spec static {discovered_type} validation (format version: {format_version}).",
            source_name=(root / file_name).as_posix() if isinstance(root, PurePath) else urljoin(str(root), file_name),
            status="failed",
            warnings=[],
        )
    else:
        rd, summary = _load_description_with_known_rd_class(rdf_content, context=context, rd_class=rd_class)

    if future_patch_warning:
        summary["warnings"] = list(summary["warnings"]) if "warnings" in summary else []
        summary["warnings"].insert(0, future_patch_warning)

    return rd, summary


def load_description_as_latest(
    rdf_content: RawStringMapping,
    *,
    context: Optional[ValidationContext] = None,
) -> Tuple[Optional[LatestResourceDescription], ValidationSummary]:
    return load_description(rdf_content, context=context, format_version=LATEST)  # type: ignore


def validate(
    rdf_content: RawStringMapping,
    context: Optional[ValidationContext] = None,
    as_format: Union[Literal["discover", "latest"], str] = DISCOVER,
) -> ValidationSummary:
    _rd, summary = load_description(rdf_content, context=context, format_version=as_format)
    return summary


def validate_legacy(
    rdf_content: RawStringMapping,  # e.g. loaded from an rdf.yaml file
    context: Optional[ValidationContext] = None,
    update_format: bool = False,  # apply auto-conversion to the latest type-specific format before validating.
) -> LegacyValidationSummary:
    """Validate a bioimage.io resource description returning the legacy validaiton summary.

    The legacy validation summary contains any errors and warnings as nested dict."""

    vs = validate(rdf_content, context, LATEST if update_format else DISCOVER)

    error = vs["errors"]
    legacy_error = nest_dict_with_narrow_first_key({e["loc"]: e["msg"] for e in error}, first_k=str)
    tb = vs.get("traceback")
    tb_list = None if tb is None else list(tb)
    return LegacyValidationSummary(
        bioimageio_spec_version=vs["bioimageio_spec_version"],
        error=legacy_error,
        name=vs["name"],
        source_name=vs["source_name"],
        status=vs["status"],
        traceback=tb_list,
        warnings={".".join(map(str, w["loc"])): w["msg"] for w in vs["warnings"]} if "warnings" in vs else {},
    )


def format_summary(summary: ValidationSummary):
    def format_loc(loc: Tuple[Union[int, str], ...]) -> str:
        if not loc:
            loc = ("root",)

        return ".".join(f"({x})" if x[0].isupper() else x for x in map(str, loc))

    es = "\n    ".join(
        e if isinstance(e, str) else f"{format_loc(e['loc'])}: {e['msg']}" for e in summary["errors"] or []
    )
    ws = "\n    ".join(f"{format_loc(w['loc'])}: {w['msg']}" for w in summary["warnings"])

    es_msg = f"errors: {es}" if es else ""
    ws_msg = f"warnings: {ws}" if ws else ""

    return f"{summary['name'].strip('.')}: {summary['status']}\nsource: {summary['source_name']}\n{es_msg}\n{ws_msg}"
