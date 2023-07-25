from __future__ import annotations
from multiprocessing import Value
from typing import Iterable, Mapping, Protocol, Type, TypeVar, Dict, Union, Tuple
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, TypeVar, Union

import pydantic

from bioimageio.spec._internal._constants import IN_PACKAGE_MESSAGE


# slimmed down version of pydantic.Field with explicit extras
def Field(  # noqa C901  NOSONAR: S1542
    default: Any = ...,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    validation_alias: Union[str, pydantic.AliasPath, pydantic.AliasChoices, None] = None,
    description: str = "",
    examples: Optional[List[Any]] = None,
    exclude: Optional[bool] = None,
    discriminator: Optional[str] = None,
    kw_only: Optional[bool] = None,
    pattern: Optional[str] = None,
    strict: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    in_package: bool = False,  # bioimageio specific
) -> Any:
    """wrap pydantic.Field"""
    return pydantic.Field(
        default,
        default_factory=default_factory,
        alias=alias,
        validation_alias=validation_alias,
        description=(IN_PACKAGE_MESSAGE if in_package else "") + description,
        examples=examples,
        exclude=exclude,
        discriminator=discriminator,
        kw_only=kw_only,
        pattern=pattern,
        strict=strict,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_length=min_length,
        max_length=max_length,
    )


K = TypeVar("K")
V = TypeVar("V")
NestedDict = Dict[K, "NestedDict[K, V] | V"]


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
