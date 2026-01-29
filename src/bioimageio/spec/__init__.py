"""bioimageio.spec --- BioImage.IO specifications in Python.

This package provides Pydantic data models for BioImage.IO resource descriptions and tools to work with such descriptions.

The BioImage.IO resource description format is resource type specific (e.g. models, datasets) and versioned.
bioimageio.spec defines and validates these specifications and is backwards compatible with previous format versions.
It also provides download/upload to/from the BioImage.IO Model Zoo at https://bioimage.io.

Note:
    For additional tools to work with BioImage.IO resources in Python, consider using the [bioimageio.core](https://bioimage-io.github.io/core-bioimage-io-python) package.
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
from ._get_conda_env import get_conda_env
from ._internal import common_nodes
from ._internal import settings as settings
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
from ._pretty_validation_errors import PRETTY_VALIDATION_ERRORS_IN_IPYNB_ENABLED
from ._upload import upload
from ._version import VERSION as __version__
from .application import AnyApplicationDescr, ApplicationDescr
from .dataset import AnyDatasetDescr, DatasetDescr
from .generic import AnyGenericDescr, GenericDescr
from .model import AnyModelDescr, ModelDescr
from .notebook import AnyNotebookDescr, NotebookDescr

BioimageioCondaEnv = conda_env.BioimageioCondaEnv
ValidationSummary = summary.ValidationSummary
InvalidDescr = common_nodes.InvalidDescr

__all__ = [
    "__version__",
    "AnyApplicationDescr",
    "AnyDatasetDescr",
    "AnyGenericDescr",
    "AnyModelDescr",
    "AnyNotebookDescr",
    "application",
    "ApplicationDescr",
    "PRETTY_VALIDATION_ERRORS_IN_IPYNB_ENABLED",
    "BioimageioCondaEnv",
    "build_description",
    "common",
    "conda_env",
    "dataset",
    "DatasetDescr",
    "dump_description",
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
