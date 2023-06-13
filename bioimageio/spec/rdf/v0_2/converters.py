import copy
from typing import Any, Dict


def _remove_slash_from_names(data: Dict[str, Any]) -> None:
    if "name" in data and isinstance(data["name"], str):
        data["name"] = data["name"].replace("/", "").replace("\\", "")

    # remove slashes in author/maintainer name
    authors = data.get("authors")
    maintainers = data.get("maintainers")
    persons: list[Any] = (authors if isinstance(authors, list) else []) + (
        maintainers if isinstance(maintainers, list) else []
    )
    for p in persons:
        if isinstance(p, dict):
            v = p.get("name")  # type: ignore
            if isinstance(v, str):
                p["name"] = v.replace("/", "").replace("\\", "")


def maybe_convert(data: Dict[str, Any]) -> Dict[str, Any]:
    # check if we have future format version
    try:
        fv = data.get("format_version", "0.2.0")
        if tuple(map(int, fv.split(".")[:2])) >= (0, 3):
            return data
    except Exception:
        pass

    data = copy.deepcopy(data)

    # we unofficially accept strings as author entries
    authors = data.get("authors")
    if isinstance(authors, list):
        data["authors"] = [{"name": a} if isinstance(a, str) else a for a in authors]  # type: ignore

    if data.get("format_version") in ("0.2.0", "0.2.1"):
        data["format_version"] = "0.2.2"

    if data.get("format_version") == "0.2.2":
        _remove_slash_from_names(data)
        data["format_version"] = "0.2.3"

    return data
