from __future__ import annotations

from pathlib import PurePath
from typing import (
    Dict,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from urllib.parse import urlparse

from pydantic import HttpUrl

from bioimageio.spec.shared.types import RelativeFilePath

K = TypeVar("K")
V = TypeVar("V")
NestedDict = Dict[K, "NestedDict[K, V] | V"]


def extract_file_name(src: Union[HttpUrl, PurePath, RelativeFilePath]) -> str:
    if isinstance(src, RelativeFilePath):
        return src.path.name
    elif isinstance(src, PurePath):
        return src.name
    else:
        return urlparse(str(src)).path.split("/")[-1]


def nest_dict(flat_dict: Dict[Tuple[K, ...], V]) -> NestedDict[K, V]:
    res: NestedDict[K, V] = {}
    for k, v in flat_dict.items():
        node = res
        for kk in k[:-1]:
            if not isinstance(node, dict):
                raise ValueError(f"nesting level collision for flat key {k} at {kk}")
            d: NestedDict[K, V] = {}
            node = node.setdefault(kk, d)

        if not isinstance(node, dict):
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
