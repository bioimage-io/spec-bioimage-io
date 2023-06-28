import collections.abc
import sys
from typing import Any, ClassVar, Dict, Generic, Iterator, Literal, Optional, Sequence, Set, TypeVar, Union

import pydantic

from bioimageio.spec.shared.types import RawValue
from bioimageio.spec.shared.validation import is_valid_raw_mapping

IncEx = Union[Set[int], Set[str], Dict[int, "IncEx"], Dict[str, "IncEx"], None]

K = TypeVar("K", bound=str)
V = TypeVar("V")

if sys.version_info < (3, 9):

    class FrozenDictBase(collections.abc.Mapping, Generic[K, V]):
        pass

else:
    FrozenDictBase = collections.abc.Mapping[K, V]


class Node(
    pydantic.BaseModel,
):
    """Subpart of a resource description"""

    model_config = pydantic.ConfigDict(
        extra="forbid",
        frozen=True,
        populate_by_name=True,
        validate_default=True,
        validate_return=True,
    )
    """pydantic model config"""

    def model_dump(
        self,
        *,
        mode: Union[Literal["json", "python"], str] = "json",  # pydantic default: "python"
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = True,  # pydantic default: False
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> Dict[str, RawValue]:
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )

    def model_dump_json(
        self,
        *,
        indent: Union[int, None] = None,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = True,  # pydantic default: False
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> str:
        return super().model_dump_json(
            indent=indent,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )


class StringNode(Node):
    """Node defined as a string"""

    _data: str

    def __str__(self):
        return self._data

    must_include: ClassVar[Sequence[str]] = ()

    @pydantic.model_serializer
    def serialize(self) -> str:
        return str(self)

    @classmethod
    def _common_assert(cls, data: Union[str, Any]):
        if not isinstance(data, str):
            raise AssertionError(f"Expected a string, but got {type(data)} instead.")

        for mi in cls.must_include:
            if mi not in data:
                raise ValueError(f"'{data}' must include {mi}")

    def __init__(self, data_string: str, /, **data: Any):
        super().__init__(**data)
        self._data = data_string


D = TypeVar("D")


class FrozenDictNode(FrozenDictBase[K, V], Node):
    model_config = {**Node.model_config, "extra": "allow"}

    def __getitem__(self, item: K) -> V:
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item) from None

    def __iter__(self) -> Iterator[K]:  # type: ignore  iterate over keys like a dict, not (key, value) tuples
        yield from self.model_fields_set  # type: ignore

    def __len__(self) -> int:
        return len(self.model_fields_set)

    def keys(self) -> Set[K]:  # type: ignore
        return set(self.model_fields_set)  # type: ignore

    def __contains__(self, key: Any):
        return key in self.model_fields_set

    def get(self, item: Any, default: D = None) -> Union[V, D]:  # type: ignore
        return getattr(self, item, default)

    @pydantic.model_validator(mode="after")
    def validate_raw_mapping(self):
        if not is_valid_raw_mapping(self):
            raise AssertionError(f"{self} contains values unrepresentable in JSON/YAML")

        return self


class Kwargs(FrozenDictNode[str, Any]):
    pass
