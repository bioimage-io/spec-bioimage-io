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

from . import _version
from . import application as application
from . import common as common
from . import conda_env as conda_env
from . import dataset as dataset
from . import generic as generic
from . import model as model
from . import notebook as notebook
from . import summary as summary
from . import utils as utils
from ._description import LatestResourceDescr as LatestResourceDescr
from ._description import ResourceDescr as ResourceDescr
from ._description import SpecificResourceDescr as SpecificResourceDescr
from ._description import build_description as build_description
from ._description import dump_description as dump_description
from ._description import validate_format as validate_format
from ._get_conda_env import get_conda_env as get_conda_env
from ._internal import common_nodes, validation_context
from ._internal import settings as settings
from ._io import load_dataset_description as load_dataset_description
from ._io import load_description as load_description
from ._io import (
    load_description_and_validate_format_only as load_description_and_validate_format_only,
)
from ._io import load_model_description as load_model_description
from ._io import save_bioimageio_yaml_only as save_bioimageio_yaml_only
from ._io import update_format as update_format
from ._io import update_hashes as update_hashes
from ._package import get_resource_package_content as get_resource_package_content
from ._package import save_bioimageio_package as save_bioimageio_package
from ._package import (
    save_bioimageio_package_as_folder as save_bioimageio_package_as_folder,
)
from ._package import (
    save_bioimageio_package_to_stream as save_bioimageio_package_to_stream,
)
from ._pretty_validation_errors import (
    PRETTY_VALIDATION_ERRORS_IN_IPYNB_ENABLED as PRETTY_VALIDATION_ERRORS_IN_IPYNB_ENABLED,
)
from ._upload import upload as upload

__version__ = _version.VERSION

# reexpose slected objects from submodules
AnyApplicationDescr = application.AnyApplicationDescr
AnyDatasetDescr = dataset.AnyDatasetDescr
AnyGenericDescr = generic.AnyGenericDescr
AnyModelDescr = model.AnyModelDescr
AnyNotebookDescr = notebook.AnyNotebookDescr
ApplicationDescr = application.ApplicationDescr
BioimageioCondaEnv = conda_env.BioimageioCondaEnv
DatasetDescr = dataset.DatasetDescr
GenericDescr = generic.GenericDescr
get_validation_context = validation_context.get_validation_context
InvalidDescr = common_nodes.InvalidDescr
ModelDescr = model.ModelDescr
NotebookDescr = notebook.NotebookDescr
ValidationContext = validation_context.ValidationContext
ValidationSummary = summary.ValidationSummary
