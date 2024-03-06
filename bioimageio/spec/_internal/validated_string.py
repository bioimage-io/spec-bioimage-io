from typing import TypeVar

from pydantic import RootModel

S = TypeVar("S", bound=str)


class ValidatedString(RootModel[S], frozen=True):
    def __str__(self) -> str:
        return self.root
