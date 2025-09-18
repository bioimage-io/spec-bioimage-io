from typing import Any, Dict

from pydantic import ConfigDict

from .._description import SpecificResourceDescr
from .._version import VERSION


def generate_json_schema() -> Dict[str, Any]:
    """generate the bioimageio specification as a JSON schema"""
    from pydantic import TypeAdapter

    spec_format_version = ".".join(VERSION.split(".")[:3])  # strip library version
    adapter: TypeAdapter[SpecificResourceDescr] = TypeAdapter(
        SpecificResourceDescr,
        config=ConfigDict(
            title=f"bioimage.io resource description {spec_format_version}"
        ),
    )

    return adapter.json_schema()
