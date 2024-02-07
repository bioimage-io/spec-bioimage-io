from typing import (
    Any,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
)

from pydantic import Field
from typing_extensions import Annotated

import bioimageio.spec
from bioimageio.spec import application, collection, dataset, generic, model, notebook
from bioimageio.spec._internal.base_nodes import InvalidDescription
from bioimageio.spec._internal.constants import DISCOVER
from bioimageio.spec._internal.types import BioimageioYamlContent, FormatVersionPlaceholder
from bioimageio.spec._internal.validation_context import ValidationContext, validation_context_var
from bioimageio.spec.summary import ValidationSummary

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
        v_module_name = f"v{fv.replace('.', '_')}"
        return getattr(type_module, v_module_name, type_module)

    v_module = get_v_module(format_version)
    rd_class = getattr(v_module, typ.capitalize() + "Descr")
    return rd_class


RD = TypeVar("RD", bound=ResourceDescr)


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
    assert rd.validation_summary is not None
    if as_format != DISCOVER and not isinstance(rd, InvalidDescription):
        discover_details = rd.validation_summary.details
        as_rd_class = _get_rd_class(typ, as_format)
        rd = as_rd_class.load(content, context=context)
        assert rd.validation_summary is not None
        rd.validation_summary.details[:0] = discover_details

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

    assert rd.validation_summary is not None
    return rd.validation_summary
