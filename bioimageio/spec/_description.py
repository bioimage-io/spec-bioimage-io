from types import MappingProxyType
from typing import Any, Literal, Optional, TypeVar, Union

from pydantic import Discriminator
from typing_extensions import Annotated

from ._build_description import DISCOVER, build_description_impl, get_rd_class_impl
from ._internal.common_nodes import InvalidDescr
from ._internal.io import BioimageioYamlContent
from ._internal.types import FormatVersionPlaceholder
from ._internal.validation_context import ValidationContext, validation_context_var
from .application import AnyApplicationDescr, ApplicationDescr
from .application.v0_2 import ApplicationDescr as ApplicationDescr02
from .application.v0_3 import ApplicationDescr as ApplicationDescr03
from .collection import AnyCollectionDescr, CollectionDescr
from .collection.v0_2 import CollectionDescr as CollectionDescr02
from .collection.v0_3 import CollectionDescr as CollectionDescr03
from .dataset import AnyDatasetDescr, DatasetDescr
from .dataset.v0_2 import DatasetDescr as DatasetDescr02
from .dataset.v0_3 import DatasetDescr as DatasetDescr03
from .generic import AnyGenericDescr, GenericDescr
from .generic.v0_2 import GenericDescr as GenericDescr02
from .generic.v0_3 import GenericDescr as GenericDescr03
from .model import AnyModelDescr, ModelDescr
from .model.v0_4 import ModelDescr as ModelDescr04
from .model.v0_5 import ModelDescr as ModelDescr05
from .notebook import AnyNotebookDescr, NotebookDescr
from .notebook.v0_2 import NotebookDescr as NotebookDescr02
from .notebook.v0_3 import NotebookDescr as NotebookDescr03
from .summary import ValidationSummary

LATEST: FormatVersionPlaceholder = "latest"
"""placeholder for the latest available format version"""


LatestResourceDescr = Union[
    Annotated[
        Union[
            ApplicationDescr,
            CollectionDescr,
            DatasetDescr,
            ModelDescr,
            NotebookDescr,
        ],
        Discriminator("type"),
    ],
    GenericDescr,
]
"""A resource description following the latest specification format"""


SpecificResourceDescr = Annotated[
    Union[
        AnyApplicationDescr,
        AnyCollectionDescr,
        AnyDatasetDescr,
        AnyModelDescr,
        AnyNotebookDescr,
    ],
    Discriminator("type"),
]
"""Any of the implemented, non-generic resource descriptions"""

ResourceDescr = Union[SpecificResourceDescr, AnyGenericDescr]
"""Any of the implemented resource descriptions"""


def dump_description(
    rd: Union[ResourceDescr, InvalidDescr], exclude_unset: bool = True
) -> BioimageioYamlContent:
    """Converts a resource to a dictionary containing only simple types that can directly be serialzed to YAML."""
    return rd.model_dump(mode="json", exclude_unset=exclude_unset)


RD = TypeVar("RD", bound=ResourceDescr)


DESCRIPTIONS_MAP = MappingProxyType(
    {
        None: MappingProxyType(
            {
                "0.2": GenericDescr02,
                "0.3": GenericDescr03,
                None: GenericDescr,
            }
        ),
        "generic": MappingProxyType(
            {
                "0.2": GenericDescr02,
                "0.3": GenericDescr03,
                None: GenericDescr,
            }
        ),
        "application": MappingProxyType(
            {
                "0.2": ApplicationDescr02,
                "0.3": ApplicationDescr03,
                None: ApplicationDescr,
            }
        ),
        "collection": MappingProxyType(
            {
                "0.2": CollectionDescr02,
                "0.3": CollectionDescr03,
                None: CollectionDescr,
            }
        ),
        "dataset": MappingProxyType(
            {
                "0.2": DatasetDescr02,
                "0.3": DatasetDescr03,
                None: DatasetDescr,
            }
        ),
        "notebook": MappingProxyType(
            {
                "0.2": NotebookDescr02,
                "0.3": NotebookDescr03,
                None: NotebookDescr,
            }
        ),
        "model": MappingProxyType(
            {
                "0.3": ModelDescr04,
                "0.4": ModelDescr04,
                "0.5": ModelDescr05,
                None: ModelDescr,
            }
        ),
    }
)


def _get_rd_class(typ: Any, format_version: Any):
    return get_rd_class_impl(typ, format_version, DESCRIPTIONS_MAP)


def build_description(
    content: BioimageioYamlContent,
    /,
    *,
    context: Optional[ValidationContext] = None,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
) -> Union[ResourceDescr, InvalidDescr]:
    return build_description_impl(
        content,
        context=context,
        format_version=format_version,
        get_rd_class=_get_rd_class,
    )


def validate_format(
    data: BioimageioYamlContent,
    /,
    *,
    format_version: Union[Literal["discover", "latest"], str] = DISCOVER,
    context: Optional[ValidationContext] = None,
) -> ValidationSummary:
    with context or validation_context_var.get():
        rd = build_description(data, format_version=format_version)

    assert rd.validation_summary is not None
    return rd.validation_summary
