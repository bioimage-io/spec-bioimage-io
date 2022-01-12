import copy
from typing import Any, Dict


def maybe_convert(data: Dict[str, Any]) -> Dict[str, Any]:
    data = copy.deepcopy(data)

    # we unofficially accept strings as author entries...
    authors = data.get("authors")
    if isinstance(authors, list):
        data["authors"] = [{"name": a} if isinstance(a, str) else a for a in authors]

    if data.get("format_version") in ("0.2.0", "0.2.1"):
        data["format_version"] = "0.2.2"

    return data
