from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, Optional, TypeVar, Union

from pydantic import Discriminator
from typing_extensions import Annotated

from ._description_impl import DISCOVER, build_description_impl, get_rd_class_impl
from ._internal.common_nodes import InvalidDescr
from ._internal.io import BioimageioYamlContent, BioimageioYamlSource
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
    """build a bioimage.io resource description from an RDF's content.

    Use `load_description` if you want to build a resource description from an rdf.yaml
    or bioimage.io zip-package.

    Args:
        content: loaded rdf.yaml file (loaded with YAML, not bioimageio.spec)
        context: validation context to use during validation
        format_version: (optional) use this argument to load the resource and
                        convert its metadata to a higher format_version

    Returns:
        An object holding all metadata of the bioimage.io resource

    """

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
    source: BioimageioYamlSource,
    *,
    output_path: Optional[Path] = None,
    target_format_version: Union[Literal["latest"], str] = LATEST,
) -> BioimageioYamlContent:
    """update a bioimageio.yaml file without validating it"""
    raise NotImplementedError("Oh no! This feature is not yet implemented")


def ensure_description_is_model(
    rd: Union[InvalidDescr, ResourceDescr],
) -> AnyModelDescr:
    if isinstance(rd, InvalidDescr):
        rd.validation_summary.display()
        raise ValueError("resource description is invalid")

    if rd.type != "model":
        rd.validation_summary.display()
        raise ValueError(
            f"expected a model resource, but got resource type '{rd.type}'"
        )

    assert not isinstance(
        rd,
        (
            GenericDescr02,
            GenericDescr03,
        ),
    )

    return rd


def ensure_description_is_dataset(
    rd: Union[InvalidDescr, ResourceDescr],
) -> AnyDatasetDescr:
    if isinstance(rd, InvalidDescr):
        rd.validation_summary.display()
        raise ValueError("resource description is invalid")

    if rd.type != "dataset":
        rd.validation_summary.display()
        raise ValueError(
            f"expected a dataset resource, but got resource type '{rd.type}'"
        )

    assert not isinstance(
        rd,
        (
            GenericDescr02,
            GenericDescr03,
        ),
    )

    return rd
