from __future__ import annotations

from typing import Any, ClassVar, Iterable, Optional, Type
from urllib.parse import urlsplit, urlunsplit

import pydantic
from pydantic import RootModel

from .validated_string import ValidatedString


class RootHttpUrl(ValidatedString):
    """An untested HTTP URL, possibly a 'URL folder' or an invalid HTTP URL"""

    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[pydantic.HttpUrl]
    _validated: pydantic.HttpUrl

    def absolute(self):
        """analog to `absolute` method of pathlib."""
        return self

    @property
    def scheme(self) -> str:
        return self._validated.scheme

    @property
    def host(self) -> Optional[str]:
        return self._validated.host

    @property
    def path(self) -> Optional[str]:
        return self._validated.path

    @property
    def parent(self) -> RootHttpUrl:
        parsed = urlsplit(str(self))
        path = list(parsed.path.split("/"))
        if (
            parsed.netloc == "zenodo.org"
            and parsed.path.startswith("/api/records/")
            and parsed.path.endswith("/content")
        ):
            path[-2:-1] = []
        else:
            path = path[:-1]

        return RootHttpUrl(
            urlunsplit(
                (
                    parsed.scheme,
                    parsed.netloc,
                    "/".join(path),
                    parsed.query,
                    parsed.fragment,
                )
            )
        )

    @property
    def parents(self) -> Iterable[RootHttpUrl]:
        """iterate over all URL parents (max 100)"""
        current = self
        for _ in range(100):
            current = current.parent
            yield current
