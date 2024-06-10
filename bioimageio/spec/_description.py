from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, Optional, TypeVar, Union

from pydantic import Discriminator
from typing_extensions import Annotated

from ._build_description import DISCOVER, build_description_impl, get_rd_class_impl
from ._internal.common_nodes import InvalidDescr
from ._internal.io import BioimageioYamlContent
from ._internal.io_utils import write_yaml
from ._internal.types import FormatVersionPlaceholder
from ._internal.validation_context import ValidationContext, validation_context_var
from .application import AnyApplicationDescr, ApplicationDescr
from .application.v0_2 import ApplicationDescr as ApplicationDescr02
from .application.v0_3 import ApplicationDescr as ApplicationDescr03
from .dataset import AnyDatasetDescr, DatasetDescr
from .dataset.v0_2 import DatasetDescr as DatasetDescr02
from .dataset.v0_3 import DatasetDescr as DatasetDescr03
from .generic import AnyGenericDescr, GenericDescr
from .generic.v0_2 import GenericDescr as GenericDescr02
from .generic.v0_3 import GenericDescr as GenericDescr03
from .model import AnyModelDescr, ModelDescr, v0_4, v0_5
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
    """validate a bioimageio.yaml file (RDF)"""
    with context or validation_context_var.get():
        rd = build_description(data, format_version=format_version)

    assert rd.validation_summary is not None
    return rd.validation_summary


def update_format(
    source: Union[
        v0_4.ModelDescr,
        GenericDescr02,
        ApplicationDescr02,
        DatasetDescr02,
        NotebookDescr02,
    ],
    *,
    output_path: Optional[Path] = None,
    target_format_version: Union[Literal["latest"], str] = LATEST,
) -> BioimageioYamlContent:
    """update an outdated resource description (partially) without validating it"""

    if isinstance(source, ModelDescr04):
        if (
            target_format_version != LATEST
            or "0.5"
            or ModelDescr05.implemented_format_version
        ):
            raise NotImplementedError(
                f"Updating model format to version {target_format_version} is supported."
                + f" (supported are: '{LATEST}', '0.5.', '{ModelDescr05.implemented_format_version}')"
            )

        updated = (
            v0_5._model_conv.convert_as_dict(  # pyright: ignore[reportPrivateUsage]
                source
            )
        )

    elif isinstance(
        source, (GenericDescr02, ApplicationDescr02, DatasetDescr02, NotebookDescr02)
    ):
        raise NotImplementedError(
            f"Updating {type(source)} not yet implemented"
        )  # TODO: Write conversion as simple dict manipulation again and expose it
    else:
        raise NotImplementedError(
            f"Updating format not implemented for {type(source)}."
        )

    if output_path is not None:
        write_yaml(updated, file=output_path)

    return updated
