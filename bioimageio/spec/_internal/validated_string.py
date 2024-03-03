from typing import TypeVar

from pydantic import RootModel

S = TypeVar("S", bound=str)


class ValidatedString(RootModel[S]):
    def __str__(self) -> str:
        return self.root
