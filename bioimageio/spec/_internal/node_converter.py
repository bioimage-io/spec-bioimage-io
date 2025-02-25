from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    Final,
    Generic,
    Type,
    Union,
    cast,
)

from typing_extensions import (
    TypeVar,
    TypeVarTuple,
    Unpack,
)

from .node import Node
from .utils import (
    assert_all_params_set_explicitly,
)
from .validated_string import ValidatedString

SRC = TypeVar("SRC", bound=Union[Node, ValidatedString])
TGT = TypeVar("TGT", bound=Node)


# converter without any additional args or kwargs:
# class Converter(Generic[SRC, TGT], ABC):
#     # src: ClassVar[Type[SRC]]
#     # tgt: ClassVar[Type[TGT]]
#     # note: the above is not yet possible, see https://github.com/python/typing/discussions/1424
#     # we therefore use an instance
#     def __init__(self, src: Type[SRC], tgt: Type[TGT], /):
#         super().__init__()
#         self.src: Final[Type[SRC]] = src
#         self.tgt: Final[Type[TGT]] = tgt

#     @abstractmethod
#     def _convert(self, src: SRC, tgt: "type[TGT | dict[str, Any]] ", /) -> "TGT | dict[str, Any]":
#         ...

#     def convert(self, source: SRC, /) -> TGT:
#         """convert `source` node

#         Args:
#             source: A bioimageio description node

#         Raises:
#             ValidationError: conversion failed
#         """
#         data = self.convert_as_dict(source)
#         return assert_all_params_set_explicitly(self.tgt)(**data)

#     def convert_as_dict(self, source: SRC) -> Dict[str, Any]:
#         return cast(Dict[str, Any], self._convert(source, dict))


# A TypeVar bound to a TypedDict seemed like a good way to add converter kwargs:
# ```
# class ConverterKwargs(TypedDict):
#     pass
# KW = TypeVar("KW", bound=ConverterKwargs, default=ConverterKwargs)
# ```
# sadly we cannot use a TypeVar bound to TypedDict and then unpack it in the Converter methods,
# see https://github.com/python/typing/issues/1399
# Therefore we use a TypeVarTuple and positional only args instead
# (We are avoiding ParamSpec for its ambiguity 'args vs kwargs')
CArgs = TypeVarTuple("CArgs")


class Converter(Generic[SRC, TGT, Unpack[CArgs]], ABC):
    # src: ClassVar[Type[SRC]]
    # tgt: ClassVar[Type[TGT]]
    # note: the above is not yet possible, see https://github.com/python/typing/discussions/1424
    # we therefore use an instance
    def __init__(self, src: Type[SRC], tgt: Type[TGT], /):
        super().__init__()
        self.src: Final[Type[SRC]] = src
        self.tgt: Final[Type[TGT]] = tgt

    @abstractmethod
    def _convert(
        self, src: SRC, tgt: "type[TGT | dict[str, Any]]", /, *args: Unpack[CArgs]
    ) -> "TGT | dict[str, Any]": ...

    # note: the following is not (yet) allowed, see https://github.com/python/typing/issues/1399
    #       we therefore use `kwargs` (and not `**kwargs`)
    # def convert(self, source: SRC, /, **kwargs: Unpack[KW]) -> TGT:
    def convert(self, source: SRC, /, *args: Unpack[CArgs]) -> TGT:
        """convert `source` node

        Args:
            source: A bioimageio description node

        Raises:
            ValidationError: conversion failed
        """
        data = self.convert_as_dict(source, *args)
        return assert_all_params_set_explicitly(self.tgt)(**data)

    def convert_as_dict(self, source: SRC, /, *args: Unpack[CArgs]) -> Dict[str, Any]:
        return cast(Dict[str, Any], self._convert(source, dict, *args))
