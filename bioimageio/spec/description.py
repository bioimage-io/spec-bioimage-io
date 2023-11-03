import traceback
from copy import deepcopy
from pathlib import PurePath
from typing import (
    Any,
    ClassVar,
    Dict,
    FrozenSet,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from urllib.parse import urljoin

import pydantic
from pydantic import Field
from pydantic_core import PydanticUndefined
from typing_extensions import Annotated, LiteralString

import bioimageio.spec
from bioimageio.spec import application, collection, dataset, generic, model, notebook
from bioimageio.spec._internal.base_nodes import ResourceDescriptionBase
from bioimageio.spec._internal.constants import DISCOVER, ERROR, INFO, LATEST, VERSION
from bioimageio.spec._internal.types import RdfContent, YamlValue
from bioimageio.spec._internal.utils import iterate_annotated_union
from bioimageio.spec._internal.validation_context import (
    InternalValidationContext,
    ValidationContext,
    get_internal_validation_context,
)
from bioimageio.spec.summary import ErrorEntry, ValidationSummary, WarningEntry

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


class InvalidDescription(ResourceDescriptionBase, extra="allow", title="An invalid resource description"):
    type: Any = "unknown"
    format_version: Any = "unknown"
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset()


def update_format(
    rdf_content: RdfContent,
    update_to_format: str = "latest",
    context: Optional[ValidationContext] = None,
) -> RdfContent:
    """Auto-update fields of a bioimage.io resource without any validation."""
    if not isinstance(rdf_content["type"], str):
        raise TypeError(f"RDF type '{rdf_content['type']}' must be a string (not '{type(rdf_content['type'])}').")

    rd_class = _get_rd_class(rdf_content["type"], update_to_format)
    if isinstance(rd_class, str):
        raise ValueError(rd_class)

    updated = dict(rdf_content)
    rd_class.convert_from_older_format(updated, get_internal_validation_context(context))
    return updated


RD = TypeVar("RD", bound=ResourceDescriptionBase)


def dump_description(rd: ResourceDescription, exclude_unset: bool = True) -> RdfContent:
    """Converts a resource to a dictionary containing only simple types that can directly be serialzed to YAML."""
    return rd.model_dump(mode="json", exclude_unset=exclude_unset)


def load_description(
    rdf_content: Union[RdfContent, ResourceDescription],
    *,
    context: Optional[ValidationContext] = None,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
) -> Union[ResourceDescription, InvalidDescription]:
    if isinstance(rdf_content, ResourceDescriptionBase):
        old_ctxt = rdf_content._internal_validation_context  # pyright: ignore[reportPrivateUsage]
        context = context or ValidationContext(root=old_ctxt["root"], file_name=old_ctxt["file_name"])
        rdf_content = dump_description(rdf_content)

    discovered_type, discovered_format_version, use_format_version = _check_type_and_format_version(rdf_content)
    if use_format_version != discovered_format_version:
        rdf_content = dict(rdf_content)
        rdf_content["format_version"] = use_format_version
        future_patch_warning = WarningEntry(
            loc=("format_version",),
            msg=f"Treated future patch version {discovered_format_version} as {use_format_version}.",
            type="alert",
        )
    else:
        future_patch_warning = None

    fv = use_format_version if format_version == DISCOVER else format_version
    rd_class = _get_rd_class(discovered_type, format_version=fv)
    context = context or ValidationContext()
    if isinstance(rd_class, str):
        rd = InvalidDescription()
        summary = ValidationSummary(
            bioimageio_spec_version=VERSION,
            errors=[ErrorEntry(loc=(), msg=rd_class, type="error")],
            name=f"bioimageio.spec static {discovered_type} validation (format version: {format_version}).",
            source_name=(context.root / context.file_name).as_posix()
            if isinstance(context.root, PurePath)
            else urljoin(str(context.root), context.file_name),
            status="failed",
            warnings=[],
        )
    else:
        rd, summary = _load_descr_with_known_rd_class(rdf_content, context=context, rd_class=rd_class)

    if future_patch_warning:
        summary.warnings.insert(0, future_patch_warning)

    assert not rd.validation_summaries, "encountered unexpected validation summary"
    rd.validation_summaries.append(summary)
    return rd


def validate_format(
    rdf_content: RdfContent,
    context: Optional[ValidationContext] = None,
    as_format: Union[Literal["discover", "latest"], str] = DISCOVER,
) -> ValidationSummary:
    rd = load_description(rdf_content, context=context, format_version=as_format)
    return rd.validation_summaries[0]


def _check_type_and_format_version(data: Union[YamlValue, RdfContent]) -> Tuple[str, str, str]:
    if not isinstance(data, dict):
        raise TypeError(f"Invalid RDF content of type '{type(data)}'")

    typ = data.get("type")
    if not isinstance(typ, str):
        raise TypeError(f"Invalid resource type '{typ}' of type {type(typ)}")

    fv = data.get("format_version")
    if not isinstance(fv, str):
        raise TypeError(f"Invalid format version '{fv}' of type {type(fv)}")

    if fv in _get_supported_format_versions(typ):
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


def _get_supported_format_versions(typ: str) -> Tuple[str, ...]:
    supported: Dict[str, List[str]] = {}
    for t, rd_class in _iterate_over_rd_classes():
        format_versions = supported.setdefault(t, [])
        ma, mi, pa = rd_class.implemented_format_version_tuple
        for p in range(pa + 1):
            format_versions.append(f"{ma}.{mi}.{p}")

    supported["model"].extend([f"0.3.{i}" for i in range(7)])  # model 0.3 can be converted
    return tuple(supported.get(typ, supported["generic"]))


def _iterate_over_rd_classes() -> Iterable[Tuple[str, Type[ResourceDescription]]]:
    for rd_class in iterate_annotated_union(ResourceDescription):
        typ = rd_class.model_fields["type"].default
        if typ is PydanticUndefined:
            typ = "generic"

        assert isinstance(typ, str)
        yield typ, rd_class


def _iterate_over_latest_rd_classes() -> Iterable[Tuple[str, Type[ResourceDescription]]]:
    for rd_class in iterate_annotated_union(LatestResourceDescription):
        typ: Any = rd_class.model_fields["type"].default
        if typ is PydanticUndefined:
            typ = "generic"

        assert isinstance(typ, str)
        yield typ, rd_class


def _load_descr_with_known_rd_class(
    rdf_content: RdfContent,
    *,
    context: ValidationContext,
    rd_class: Type[RD],
) -> Tuple[Union[RD, InvalidDescription], ValidationSummary]:
    raw_rd = deepcopy(dict(rdf_content))
    rd, errors, tb, val_warnings = _load_descr_impl(
        rd_class,
        raw_rd,
        get_internal_validation_context(context.model_dump(), warning_level=ERROR),
    )  # ignore any warnings using warning level 'ERROR'/'CRITICAL' on first loading attempt

    assert not val_warnings, f"already got warnings: {val_warnings}"
    _, error2, tb2, val_warnings = _load_descr_impl(
        rd_class, raw_rd, get_internal_validation_context(context.model_dump(), warning_level=INFO)
    )
    assert not error2 or isinstance(rd, InvalidDescription), f"decreasing warning level caused errors: {error2}"
    assert not tb2 or isinstance(rd, InvalidDescription), f"decreasing warning level lead to error traceback: {tb2}"

    summary = ValidationSummary(
        bioimageio_spec_version=VERSION,
        errors=errors,
        name=f"bioimageio.spec static validation of {rd.type} (format version: {rd.format_version}).",
        source_name=(context.root / context.file_name).as_posix()
        if isinstance(context.root, PurePath)
        else urljoin(str(context.root), context.file_name),
        status="failed" if errors else "passed",
        warnings=val_warnings,
        traceback=tb,
    )

    return rd, summary


def _load_descr_impl(
    rd_class: Type[RD], rdf_content: RdfContent, context: InternalValidationContext
) -> Tuple[Union[RD, InvalidDescription], List[ErrorEntry], List[str], List[WarningEntry]]:
    rd: Union[RD, InvalidDescription, None] = None
    val_errors: List[ErrorEntry] = []
    val_warnings: List[WarningEntry] = []
    tb: List[str] = []

    try:
        rd = rd_class.model_validate(rdf_content, context=dict(context))
    except pydantic.ValidationError as e:
        for ee in e.errors(include_url=False):
            if (severity := ee.get("ctx", {}).get("severity", ERROR)) < ERROR:
                val_warnings.append(WarningEntry(loc=ee["loc"], msg=ee["msg"], type=ee["type"], severity=severity))
            else:
                val_errors.append(ErrorEntry(loc=ee["loc"], msg=ee["msg"], type=ee["type"]))
    except Exception as e:
        val_errors.append(ErrorEntry(loc=(), msg=str(e), type=type(e).__name__))
        tb = traceback.format_tb(e.__traceback__)

    if rd is None:
        try:
            rd = InvalidDescription(**rdf_content)
        except Exception:
            resource_type = rd_class.model_fields["type"].default
            format_version = rd_class.implemented_format_version
            rd = InvalidDescription(type=resource_type, format_version=format_version)

    return rd, val_errors, tb, val_warnings
