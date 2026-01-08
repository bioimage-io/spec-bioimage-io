import difflib
import re
from typing import Any, Dict, Optional, Tuple

from loguru import logger
from pydantic import ConfigDict

from .._description import DESCRIPTIONS_MAP, SpecificResourceDescr
from .._version import VERSION
from .type_guards import is_dict, is_list


def _patch_desccription(
    json_schema: Dict[str, Any], path: Tuple[str, ...] = ()
) -> None:
    """Patch descriptions:

    - replace mkdocstrings cross-reference syntax [object][] by `object`
    """
    if isinstance(descr := json_schema.get("description"), str) and descr:
        # Replace markdown link references like [object][] with `object`
        new_descr = re.sub(r"\[([^\]]+)\]\[\]", r"`\1`", descr)
        if descr != new_descr:
            diff = difflib.Differ().compare(descr.splitlines(), new_descr.splitlines())
            logger.debug(f"updated {'.'.join(path)}:\n" + "\n".join(diff))
            json_schema["description"] = new_descr

    for k, v in json_schema.items():
        if is_dict(v):
            _patch_desccription(v, path + (str(k),))
        elif is_list(v):
            for index, item in enumerate(v):
                if is_dict(item):
                    _patch_desccription(item, path + (str(k), str(index)))


def generate_json_schema(
    type_format: Optional[Tuple[str, str]] = None,
) -> Dict[str, Any]:
    """generate the bioimageio specification as a JSON schema"""
    from pydantic import TypeAdapter

    spec_format_version = ".".join(VERSION.split(".")[:3])  # strip library version
    if type_format is None:
        adapter: TypeAdapter[Any] = TypeAdapter(
            SpecificResourceDescr,
            config=ConfigDict(
                title=f"bioimage.io resource description {spec_format_version}"
            ),
        )
    else:
        typ, format_version = type_format
        rd_class = DESCRIPTIONS_MAP[typ][format_version]
        adapter = TypeAdapter(rd_class)

    json_schema = adapter.json_schema()
    _patch_desccription(json_schema)
    return json_schema
