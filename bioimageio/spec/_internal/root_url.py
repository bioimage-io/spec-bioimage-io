from __future__ import annotations

from typing import Any, ClassVar, Optional, Type
from urllib.parse import urlsplit, urlunsplit

import pydantic
from pydantic import RootModel

from .validated_string import ValidatedString


class RootHttpUrl(ValidatedString):
    """A 'URL folder', possibly an invalid http URL"""

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
