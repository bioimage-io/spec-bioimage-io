from typing import Any, Dict, Literal, Sequence, Union

import pydantic

from bioimageio.spec.shared.types_ import RawValue
from bioimageio.spec.shared.validation import is_valid_raw_mapping

IncEx = Union[set[int], set[str], dict[int, "IncEx"], dict[str, "IncEx"], None]


class Node(
    pydantic.BaseModel,
):
    """Subpart of a resource description"""

    model_config = dict(
        populate_by_name=True,
        extra=pydantic.Extra.forbid,
        frozen=True,
    )
    """pydantic model config"""

    @pydantic.field_validator("*", mode="after")
    def unique_sequence_entries(cls, value: Union[Sequence[Any], Any]):
        if isinstance(value, (list, tuple)):
            if len(value) != len(set(value)):
                raise ValueError("Expected unique values")

        return value

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


class FrozenDictNode(Node):
    model_config = {**Node.model_config, **dict(extra=pydantic.Extra.allow)}

    def __getitem__(self, item: str):
        return getattr(self, item)

    def keys(self):
        return self.model_fields_set

    @pydantic.model_validator(mode="after")
    def validate_raw_mapping(self):
        if not is_valid_raw_mapping(self):
            raise AssertionError(f"{self} contains values unrepresentable in JSON/YAML")

        return self


class Kwargs(FrozenDictNode):
    pass
