from __future__ import annotations
from typing import Union, Any, Mapping, Sequence
from typing_extensions import TypeGuard, TypeAlias

JsonLeafValue: TypeAlias = Union[int, float, str, bool, None]
JsonObject: TypeAlias = Mapping[Union[str, int], "JsonValue"]
JsonArray: TypeAlias = Sequence["JsonValue"]
JsonValue: TypeAlias = Union[JsonLeafValue, JsonArray, JsonObject]

class NotJsonvalue(Exception):
    def __init__(self, value: Any) -> None:
        super().__init__("Not a json value: {value}")

####################################
def is_json_leaf_value(value: Any) -> TypeGuard[JsonLeafValue]:
    return isinstance(value, (int, float, str, bool)) or value is None

def is_json_sequence(value: Any) -> TypeGuard[Sequence[JsonValue]]:
    return isinstance(value, Sequence) and \
        all(is_json_value(item) for item in value) #pyright: ignore [reportUnknownVariableType]

def is_json_object(value: Any) -> TypeGuard[JsonObject]:
    return isinstance(value, Mapping) and \
        all(
            isinstance(key, (str, int)) and
            is_json_value(val) for key, val in value.items() #pyright: ignore [reportUnknownVariableType]
        )

def is_json_value(value: Any) -> TypeGuard[JsonValue]:
    return is_json_leaf_value(value) or is_json_sequence(value) or is_json_object(value)
