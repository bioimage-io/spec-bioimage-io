from typing import Any, Hashable, Union

import pydantic


class Node(
    pydantic.BaseModel,
):
    """Subpart of a resource description"""

    model_config = dict(
        extra=pydantic.Extra.forbid,
        frozen=True,
    )
    """pydantic model config"""

    @pydantic.field_validator("*", mode="after")
    def unique_sequence_entries(cls, value: Union[tuple[Hashable, ...], list[Hashable], Any]):
        if isinstance(value, (tuple, list)) and len(value) != len(set(value)):
            raise ValueError("Expected unique values")

        return value
