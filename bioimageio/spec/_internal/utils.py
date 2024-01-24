from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Type, TypeVar, Union, cast
from urllib.parse import urlsplit, urlunsplit

from pydantic import AnyUrl, HttpUrl
from typing_extensions import Annotated

K = TypeVar("K")
V = TypeVar("V")
NestedDict = Dict[K, "NestedDict[K, V] | V"]


if sys.version_info < (3, 9):

    def files(package_name: str):
        assert package_name == "bioimageio.spec", package_name
        return Path(__file__).parent.parent

else:
    from importlib.resources import files as files

_annot_type = type(Annotated[int, "int"])


def get_parent_url(url: HttpUrl) -> HttpUrl:
    parsed = urlsplit(str(url))
    path = list(parsed.path.split("/"))
    if parsed.netloc == "zenodo.org" and parsed.path.startswith("/api/records/") and parsed.path.endswith("/content"):
        path[-2:-1] = cast(List[str], [])
    else:
        path = path[:-1]

    return AnyUrl(urlunsplit((parsed.scheme, parsed.netloc, "/".join(path), parsed.query, parsed.fragment)))


def nest_dict(flat_dict: Dict[Tuple[K, ...], V]) -> NestedDict[K, V]:
    res: NestedDict[K, V] = {}
    for k, v in flat_dict.items():
        node: Union[Dict[K, Union[NestedDict[K, V], V]], NestedDict[K, V]] = res
        for kk in k[:-1]:
            if not isinstance(node, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
                raise ValueError(f"nesting level collision for flat key {k} at {kk}")
            d: NestedDict[K, V] = {}
            node = node.setdefault(kk, d)  # type: ignore

        if not isinstance(node, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError(f"nesting level collision for flat key {k}")

        node[k[-1]] = v

    return res


FirstK = TypeVar("FirstK")


def nest_dict_with_narrow_first_key(
    flat_dict: Dict[Tuple[K, ...], V], first_k: Type[FirstK]
) -> Dict[FirstK, "NestedDict[K, V] | V"]:
    """convenience function to annotate a special version of a NestedDict.
    Root level keys are of a narrower type than the nested keys. If not a ValueError is raisd."""
    nested = nest_dict(flat_dict)
    invalid_first_keys = [k for k in nested if not isinstance(k, first_k)]
    if invalid_first_keys:
        raise ValueError(f"Invalid root level keys: {invalid_first_keys}")

    return nested  # type: ignore


def unindent(text: str, ignore_first_line: bool = False):
    """remove minimum count of spaces at beginning of each line.

    Args:
        text: indented text
        ignore_first_line: allows to correctly unindent doc strings
    """
    first = int(ignore_first_line)
    lines = text.split("\n")
    filled_lines = [line for line in lines[first:] if line]
    if len(filled_lines) < 2:
        return "\n".join(line.strip() for line in lines)

    indent = min(len(line) - len(line.lstrip(" ")) for line in filled_lines)
    return "\n".join(lines[:first] + [line[indent:] for line in lines[first:]])
