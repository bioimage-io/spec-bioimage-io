from types import MappingProxyType
from typing import Any, Literal, Optional, TypeVar, Union, overload

from pydantic import Discriminator
from typing_extensions import Annotated

from bioimageio.spec._internal.validation_context import ValidationContext

from ._description_impl import DISCOVER, build_description_impl, get_rd_class_impl
from ._internal.common_nodes import InvalidDescr
from ._internal.io import BioimageioYamlContent, BioimageioYamlContentView
from ._internal.types import FormatVersionPlaceholder
from ._internal.validation_context import get_validation_context
from .application import (
    AnyApplicationDescr,
    ApplicationDescr,
    ApplicationDescr_v0_2,
    ApplicationDescr_v0_3,
)
from .dataset import AnyDatasetDescr, DatasetDescr, DatasetDescr_v0_2, DatasetDescr_v0_3
from .generic import AnyGenericDescr, GenericDescr, GenericDescr_v0_2, GenericDescr_v0_3
from .model import AnyModelDescr, ModelDescr, ModelDescr_v0_4, ModelDescr_v0_5
from .notebook import (
    AnyNotebookDescr,
    NotebookDescr,
    NotebookDescr_v0_2,
    NotebookDescr_v0_3,
)
from .summary import ValidationSummary

LATEST: Literal["latest"] = "latest"
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
    rd: Union[ResourceDescr, InvalidDescr],
    /,
    *,
    exclude_unset: bool = True,
    exclude_defaults: bool = False,
) -> BioimageioYamlContent:
    """Converts a resource to a dictionary containing only simple types that can directly be serialzed to YAML.

    Args:
        rd: bioimageio resource description
        exclude_unset: Exclude fields that have not explicitly be set.
        exclude_defaults: Exclude fields that have the default value (even if set explicitly).
    """
    return rd.model_dump(
        mode="json", exclude_unset=exclude_unset, exclude_defaults=exclude_defaults
    )


RD = TypeVar("RD", bound=ResourceDescr)


LATEST_DESCRIPTIONS_MAP = MappingProxyType(
    {
        None: GenericDescr,
        "generic": GenericDescr,
        "application": ApplicationDescr,
        "dataset": DatasetDescr,
        "notebook": NotebookDescr,
        "model": ModelDescr,
    }
)
DESCRIPTIONS_MAP = MappingProxyType(
    {
        None: MappingProxyType(
            {
                "0.2": GenericDescr_v0_2,
                "0.3": GenericDescr_v0_3,
                "latest": GenericDescr,
            }
        ),
        "generic": MappingProxyType(
            {
                "0.2": GenericDescr_v0_2,
                "0.3": GenericDescr_v0_3,
                "latest": GenericDescr,
            }
        ),
        "application": MappingProxyType(
            {
                "0.2": ApplicationDescr_v0_2,
                "0.3": ApplicationDescr_v0_3,
                "latest": ApplicationDescr,
            }
        ),
        "dataset": MappingProxyType(
            {
                "0.2": DatasetDescr_v0_2,
                "0.3": DatasetDescr_v0_3,
                "latest": DatasetDescr,
            }
        ),
        "notebook": MappingProxyType(
            {
                "0.2": NotebookDescr_v0_2,
                "0.3": NotebookDescr_v0_3,
                "latest": NotebookDescr,
            }
        ),
        "model": MappingProxyType(
            {
                "0.3": ModelDescr_v0_4,
                "0.4": ModelDescr_v0_4,
                "0.5": ModelDescr_v0_5,
                "latest": ModelDescr,
            }
        ),
    }
)
"""A mapping to determine the appropriate Description class
 for a given **type** and **format_version**."""


def _get_rd_class(typ: Any, format_version: Any, fallback_to_latest: bool):
    return get_rd_class_impl(
        typ, format_version, DESCRIPTIONS_MAP, fallback_to_latest=fallback_to_latest
    )


@overload
def build_description(
    content: BioimageioYamlContentView,
    /,
    *,
    context: Optional[ValidationContext] = None,
    format_version: Literal["latest"],
) -> Union[LatestResourceDescr, InvalidDescr]: ...


@overload
def build_description(
    content: BioimageioYamlContentView,
    /,
    *,
    context: Optional[ValidationContext] = None,
    format_version: Union[FormatVersionPlaceholder, str] = DISCOVER,
) -> Union[ResourceDescr, InvalidDescr]: ...


def build_description(
    content: BioimageioYamlContentView,
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
        format_version:
            (optional) use this argument to load the resource and
            convert its metadata to a higher format_version.
            Note:
            - Use "latest" to convert to the latest available format version.
            - Use "discover" to use the format version specified in the RDF.
            - Only considers major.minor format version, ignores patch version.
            - Conversion to lower format versions is not supported.

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
    """Validate a dictionary holding a bioimageio description.
    See `bioimagieo.spec.load_description_and_validate_format_only`
    to validate a file source.

    Args:
        data: Dictionary holding the raw bioimageio.yaml content.
        format_version:
            Format version to (update to and) use for validation.
            Note:
            - Use "latest" to convert to the latest available format version.
            - Use "discover" to use the format version specified in the RDF.
            - Only considers major.minor format version, ignores patch version.
            - Conversion to lower format versions is not supported.
        context: Validation context, see `bioimagieo.spec.ValidationContext`

    Note:
        Use `bioimagieo.spec.load_description_and_validate_format_only` to validate a
        file source instead of loading the YAML content and creating the appropriate
        `ValidationContext`.

        Alternatively you can use `bioimagieo.spec.load_description` and access the
        `validation_summary` attribute of the returned object.
    """
    with context or get_validation_context():
        rd = build_description(data, format_version=format_version)

    assert rd.validation_summary is not None
    return rd.validation_summary


def ensure_description_is_model(
    rd: Union[InvalidDescr, ResourceDescr],
) -> AnyModelDescr:
    """
    Raises:
        ValueError: for invalid or non-model resources
    """
    if isinstance(rd, InvalidDescr):
        rd.validation_summary.display()
        raise ValueError(f"Invalid {rd.type} description")

    if rd.type != "model":
        rd.validation_summary.display()
        raise ValueError(
            f"Expected a model resource, but got resource type '{rd.type}'"
        )

    assert not isinstance(
        rd,
        (
            GenericDescr_v0_2,
            GenericDescr_v0_3,
        ),
    )

    return rd


def ensure_description_is_dataset(
    rd: Union[InvalidDescr, ResourceDescr],
) -> AnyDatasetDescr:
    if isinstance(rd, InvalidDescr):
        rd.validation_summary.display()
        raise ValueError(f"Invalid {rd.type} description.")

    if rd.type != "dataset":
        rd.validation_summary.display()
        raise ValueError(
            f"Expected a dataset resource, but got resource type '{rd.type}'"
        )

    assert not isinstance(
        rd,
        (
            GenericDescr_v0_2,
            GenericDescr_v0_3,
        ),
    )

    return rd
