from typing import Any, Dict, Optional, Tuple

from pydantic import ConfigDict

from .._description import DESCRIPTIONS_MAP, SpecificResourceDescr
from .._version import VERSION


def generate_json_schema(
    type_format: Optional[Tuple[str, str]] = None,
) -> Dict[str, Any]:
    """generate the bioimageio specification as a JSON schema"""
    from pydantic import TypeAdapter

    spec_format_version = ".".join(VERSION.split(".")[:3])  # strip library version
    if type_format is None:
        adapter: TypeAdapter[SpecificResourceDescr] = TypeAdapter(
            SpecificResourceDescr,
            config=ConfigDict(
                title=f"bioimage.io resource description {spec_format_version}"
            ),
        )
    else:
        typ, format_version = type_format
        rd_class = DESCRIPTIONS_MAP[typ][format_version]
        adapter = TypeAdapter(
            rd_class,
            config=ConfigDict(
                title=f"bioimage.io resource description {spec_format_version} - {typ} v{format_version}"
            ),
        )

    return adapter.json_schema()
