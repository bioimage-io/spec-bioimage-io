"""
.. include:: ../../README.md
"""

from . import (
    application,
    common,
    conda_env,
    dataset,
    generic,
    model,
    pretty_validation_errors,
    summary,
    utils,
)
from ._description import (
    LatestResourceDescr,
    ResourceDescr,
    SpecificResourceDescr,
    build_description,
    dump_description,
    validate_format,
)
from ._internal import settings
from ._internal.common_nodes import InvalidDescr
from ._internal.constants import VERSION
from ._internal.validation_context import ValidationContext
from ._io import (
    load_dataset_description,
    load_description,
    load_description_and_validate_format_only,
    load_model_description,
    save_bioimageio_yaml_only,
)
from ._package import (
    get_resource_package_content,
    save_bioimageio_package,
    save_bioimageio_package_as_folder,
    save_bioimageio_package_to_stream,
)
from .application import AnyApplicationDescr, ApplicationDescr
from .dataset import AnyDatasetDescr, DatasetDescr
from .generic import AnyGenericDescr, GenericDescr
from .model import AnyModelDescr, ModelDescr
from .notebook import AnyNotebookDescr, NotebookDescr
from .pretty_validation_errors import enable_pretty_validation_errors_in_ipynb
from .summary import ValidationSummary

__version__ = VERSION

__all__ = [
    "__version__",
    "AnyApplicationDescr",
    "AnyDatasetDescr",
    "AnyGenericDescr",
    "AnyModelDescr",
    "AnyNotebookDescr",
    "application",
    "ApplicationDescr",
    "build_description",
    "common",
    "conda_env",
    "dataset",
    "DatasetDescr",
    "dump_description",
    "enable_pretty_validation_errors_in_ipynb",
    "generic",
    "GenericDescr",
    "get_resource_package_content",
    "InvalidDescr",
    "LatestResourceDescr",
    "load_dataset_description",
    "load_description_and_validate_format_only",
    "load_description",
    "load_model_description",
    "model",
    "ModelDescr",
    "NotebookDescr",
    "pretty_validation_errors",
    "ResourceDescr",
    "save_bioimageio_package_as_folder",
    "save_bioimageio_package_to_stream",
    "save_bioimageio_package",
    "save_bioimageio_yaml_only",
    "settings",
    "SpecificResourceDescr",
    "summary",
    "utils",
    "validate_format",
    "ValidationContext",
    "ValidationSummary",
]
