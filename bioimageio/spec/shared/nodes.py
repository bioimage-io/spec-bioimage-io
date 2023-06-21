from typing import TYPE_CHECKING, Any, Hashable, Union
from typing_extensions import Literal

import pydantic

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
    def unique_sequence_entries(cls, value: Union[tuple[Hashable, ...], list[Hashable], Any]):
        if isinstance(value, (tuple, list)) and len(value) != len(set(value)):
            raise ValueError("Expected unique values")

        return value

    def model_dump(
        self,
        *,
        mode: str = "python",
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = True,  # pydantic default: False
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
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
