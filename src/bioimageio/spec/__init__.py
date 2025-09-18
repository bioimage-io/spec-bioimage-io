"""
.. include:: ../../README.md
"""

# ruff: noqa: E402
from loguru import logger

logger.disable("bioimageio.spec")

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
from ._get_conda_env import BioimageioCondaEnv, get_conda_env
from ._internal import settings
from ._internal.common_nodes import InvalidDescr
from ._internal.validation_context import ValidationContext, get_validation_context
from ._io import (
    load_dataset_description,
    load_description,
    load_description_and_validate_format_only,
    load_model_description,
    save_bioimageio_yaml_only,
    update_format,
    update_hashes,
)
from ._package import (
    get_resource_package_content,
    save_bioimageio_package,
    save_bioimageio_package_as_folder,
    save_bioimageio_package_to_stream,
)
from ._upload import upload
from ._version import VERSION as __version__
from .application import AnyApplicationDescr, ApplicationDescr
from .dataset import AnyDatasetDescr, DatasetDescr
from .generic import AnyGenericDescr, GenericDescr
from .model import AnyModelDescr, ModelDescr
from .notebook import AnyNotebookDescr, NotebookDescr
from .pretty_validation_errors import enable_pretty_validation_errors_in_ipynb
from .summary import ValidationSummary

__all__ = [
    "__version__",
    "AnyApplicationDescr",
    "AnyDatasetDescr",
    "AnyGenericDescr",
    "AnyModelDescr",
    "AnyNotebookDescr",
    "application",
    "ApplicationDescr",
    "BioimageioCondaEnv",
    "build_description",
    "common",
    "conda_env",
    "dataset",
    "DatasetDescr",
    "dump_description",
    "enable_pretty_validation_errors_in_ipynb",
    "generic",
    "GenericDescr",
    "get_conda_env",
    "get_resource_package_content",
    "get_validation_context",
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
    "update_format",
    "update_hashes",
    "upload",
    "utils",
    "validate_format",
    "ValidationContext",
    "ValidationSummary",
]
