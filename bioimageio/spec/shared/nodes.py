from abc import ABC
from typing import Any, ClassVar, Dict, Generator, Iterable, Iterator, KeysView, Literal, Sequence, Set, Tuple, Union

import pydantic
import collections.abc

from bioimageio.spec.shared.types import RawValue
from bioimageio.spec.shared.validation import is_valid_raw_mapping

IncEx = Union[set[int], set[str], dict[int, "IncEx"], dict[str, "IncEx"], None]


class Node(
    pydantic.BaseModel,
):
    """Subpart of a resource description"""

    model_config = dict(
        populate_by_name=True,
        extra="forbid",
        frozen=True,
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


class FrozenDictNode(collections.abc.Mapping[str, Any], Node):
    model_config = {**Node.model_config, "extra": "allow"}

    def __getitem__(self, item: str):
        return getattr(self, item, None)

    def __iter__(self) -> Iterator[str]:  # type: ignore
        yield from self.model_fields_set

    def __len__(self) -> int:
        return len(self.model_fields_set)

    def keys(self) -> Set[str]:  # type: ignore
        return set(self.model_fields_set)

    @pydantic.model_validator(mode="after")
    def validate_raw_mapping(self):
        if not is_valid_raw_mapping(self):
            raise AssertionError(f"{self} contains values unrepresentable in JSON/YAML")

        return self


class Kwargs(FrozenDictNode):
    pass
