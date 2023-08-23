from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Iterator, Tuple, Type, TypeVar, Union, get_args, get_origin

from typing_extensions import Annotated

K = TypeVar("K")
V = TypeVar("V")
NestedDict = Dict[K, "NestedDict[K, V] | V"]


if sys.version_info < (3, 9):

    def files(package_name: str):
        assert package_name == "bioimageio.spec"
        return Path(__file__).parent.parent

else:
    from importlib.resources import files  # type: ignore

_annot_type = type(Annotated[int, "int"])


def iterate_annotated_union(typ: type) -> Iterator[Any]:
    """iterate over all type arguments in a nested combination of Annotation and Union

    >>> U = Union[Annotated[int, "int"], Annotated[str, "str"]]
    >>> A = Annotated[U, "union"]
    >>> list(iterate_annotated_union(U))
    [<class 'int'>, <class 'str'>]
    >>> list(iterate_annotated_union(A))
    [<class 'int'>, <class 'str'>]
    """
    if get_origin(typ) is Union:
        for t in get_args(typ):
            yield from iterate_annotated_union(t)
    elif isinstance(typ, _annot_type):
        yield from iterate_annotated_union(get_args(typ)[0])
    else:
        yield typ


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
