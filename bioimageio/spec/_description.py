from typing import (
    Any,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from pydantic import Field, ValidationError
from typing_extensions import Annotated

import bioimageio.spec
from bioimageio.spec import application, collection, dataset, generic, model, notebook
from bioimageio.spec._internal.base_nodes import InvalidDescription
from bioimageio.spec._internal.constants import DISCOVER, ERROR, VERSION
from bioimageio.spec._internal.types import BioimageioYamlContent, FormatVersionPlaceholder, RelativeFilePath
from bioimageio.spec._internal.validation_context import ValidationContext, validation_context_var
from bioimageio.spec.summary import ErrorEntry, ValidationSummary, WarningEntry

_ResourceDescr_v0_2 = Union[
    Annotated[
        Union[
            application.v0_2.ApplicationDescr,
            collection.v0_2.CollectionDescr,
            dataset.v0_2.DatasetDescr,
            model.v0_4.ModelDescr,
            notebook.v0_2.NotebookDescr,
        ],
        Field(discriminator="type"),
    ],
    generic.v0_2.GenericDescr,
]
"""A resource description following the 0.2.x (model: 0.4.x) specification format"""

_ResourceDescription_v0_3 = Union[
    Annotated[
        Union[
            application.v0_3.ApplicationDescr,
            collection.v0_3.CollectionDescr,
            dataset.v0_3.DatasetDescr,
            model.v0_5.ModelDescr,
            notebook.v0_3.NotebookDescr,
        ],
        Field(discriminator="type"),
    ],
    generic.v0_3.GenericDescr,
]
"""A resource description following the 0.3.x (model: 0.5.x) specification format"""

LatestResourceDescr = _ResourceDescription_v0_3
"""A resource description following the latest specification format"""


SpecificResourceDescr = Annotated[
    Union[
        application.AnyApplicationDescr,
        collection.AnyCollectionDescr,
        dataset.AnyDatasetDescr,
        model.AnyModelDescr,
        notebook.AnyNotebookDescr,
    ],
    Field(discriminator="type"),
]
"""Any of the implemented, non-generic resource descriptions"""

ResourceDescr = Union[
    SpecificResourceDescr,
    generic.AnyGenericDescr,
]
"""Any of the implemented resource descriptions"""


def dump_description(rd: ResourceDescr, exclude_unset: bool = True) -> BioimageioYamlContent:
    """Converts a resource to a dictionary containing only simple types that can directly be serialzed to YAML."""
    return rd.model_dump(mode="json", exclude_unset=exclude_unset)


def _get_rd_class(typ: Any, format_version: Any) -> Type[ResourceDescr]:
    if not isinstance(typ, str) or not hasattr(bioimageio.spec, typ):
        typ = "generic"
        type_module = bioimageio.spec.generic
    else:
        type_module = getattr(bioimageio.spec, typ)

    def get_v_module(fv: Any):
        if not isinstance(fv, str):
            return type_module

        if (ndots := fv.count(".")) == 0:
            fv = fv + ".0"
        elif ndots == 2:
            fv = fv[: fv.rfind(".")]
        else:
            return type_module

        assert fv.count(".") == 1
        v_module_name = f"v{fv[:fv.rfind('.')].replace('.', '_')}"
        return getattr(type_module, v_module_name, type_module)

    v_module = get_v_module(format_version)
    rd_class = getattr(v_module, typ.capitalize() + "Descr")
    return rd_class


RD = TypeVar("RD", bound=ResourceDescr)


def _convert_descr(
    descr: ResourceDescr, target_class: Type[RD]
) -> Tuple[Union[RD, InvalidDescription], List[ErrorEntry], List[WarningEntry]]:
    conversion_errors: List[ErrorEntry] = []
    conversion_warnings: List[WarningEntry] = []
    try:
        converted = target_class.from_other_descr(descr)  # type: ignore
    except ValidationError as e:
        for ee in e.errors(include_url=False):
            loc = ee["loc"]
            msg = ee["msg"]
            etype = ee["type"]
            if (severity := ee.get("ctx", {}).get("severity", ERROR)) < ERROR:
                conversion_warnings.append(WarningEntry(loc=loc, msg=msg, type=etype, severity=severity))
            else:
                conversion_errors.append(ErrorEntry(loc=loc, msg=msg, type=etype))

        if conversion_errors:
            converted = InvalidDescription(**dict(descr))
        else:
            with validation_context_var.get().model_copy(update=dict(warning_level=ERROR)):
                converted, conversion_errors, _ = _convert_descr(descr, target_class)
    except Exception as e:
        conversion_errors.append(
            ErrorEntry(loc=(), msg=f"failed to convert due to {type(e)}: {e}", type="conversion_error")
        )
        converted = InvalidDescription(**dict(descr))

    return converted, conversion_errors, conversion_warnings


def build_description(
    content: BioimageioYamlContent,
    /,
    *,
    context: Optional[ValidationContext] = None,
    as_format: Union[FormatVersionPlaceholder, str] = DISCOVER,
) -> Union[ResourceDescr, InvalidDescription]:
    context = context or validation_context_var.get()
    if not isinstance(content, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        # "Invalid content of type '{type(content)}'"
        rd_class = bioimageio.spec.GenericDescr

    typ = content.get("type")
    rd_class = _get_rd_class(typ, content.get("format_version"))

    rd = rd_class.load(content, context=context)
    if as_format != DISCOVER and not isinstance(rd, InvalidDescription):
        as_rd_class = _get_rd_class(typ, as_format)
        rd, conversion_errors, conversion_warnings = _convert_descr(rd, as_rd_class)

        conversion_summary = ValidationSummary(
            bioimageio_spec_version=VERSION,
            errors=conversion_errors,
            name=f"bioimageio.spec conversion from {typ} {rd_class.implemented_format_version} to {typ} {as_rd_class.implemented_format_version}.",
            source_name=str(RelativeFilePath(context.file_name).get_absolute(context.root)),
            status="failed" if conversion_errors else "passed",
            warnings=conversion_warnings,
        )
        rd.validation_summaries.append(conversion_summary)

    return rd


def validate_format(
    data: BioimageioYamlContent,
    /,
    *,
    as_format: Union[Literal["discover", "latest"], str] = DISCOVER,
    context: Optional[ValidationContext] = None,
) -> ValidationSummary:
    with context or validation_context_var.get():
        rd = build_description(data, as_format=as_format)

    return rd.validation_summaries[0]
