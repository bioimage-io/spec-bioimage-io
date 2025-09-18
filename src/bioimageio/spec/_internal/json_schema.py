from typing import Any, Dict

from pydantic import ConfigDict

from .. import __version__
from .._description import SpecificResourceDescr


def generate_json_schema() -> Dict[str, Any]:
    """generate the bioimageio specification as a JSON schema"""
    from pydantic import TypeAdapter

    adapter: TypeAdapter[SpecificResourceDescr] = TypeAdapter(
        SpecificResourceDescr,
        config=ConfigDict(title=f"bioimage.io resource description {__version__}"),
    )

    return adapter.json_schema()
