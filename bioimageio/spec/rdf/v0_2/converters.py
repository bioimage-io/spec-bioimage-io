from typing import Any, Dict


def maybe_convert(data: Dict[str, Any]) -> Dict[str, Any]:
    # we unofficially accept strings as author entries...
    authors = data.get("authors")
    if isinstance(authors, list):
        data["authors"] = [{"name": a} if isinstance(a, str) else a for a in authors]

    return data
