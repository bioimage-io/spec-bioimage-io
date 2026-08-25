from __future__ import annotations

from abc import ABC
from pathlib import PurePosixPath
from typing import Any, ClassVar, Generic, Iterable, TypeVar
from urllib.parse import urlsplit, urlunsplit

import pydantic
from pydantic import RootModel

from .validated_string import ValidatedString

ValidatedType = TypeVar("ValidatedType", pydantic.HttpUrl, pydantic.FtpUrl)


class _RootUrl(ValidatedString, ABC, Generic[ValidatedType]):
    """An untested HTTP URL, possibly a 'URL folder' or an invalid HTTP URL"""

    root_model: ClassVar[type[RootModel[Any]]]
    _validated: ValidatedType

    def absolute(self):
        """analog to `absolute` method of pathlib."""
        return self

    @property
    def scheme(self) -> str:
        return self._validated.scheme

    @property
    def host(self) -> str | None:
        return self._validated.host

    @property
    def path(self) -> str | None:
        return self._validated.path

    @property
    def suffix(self) -> str:
        if self.path is None:
            return ""
        else:
            return PurePosixPath(self.path).suffix

    @property
    def suffixes(self) -> list[str]:
        if self.path is None:
            return []
        else:
            return PurePosixPath(self.path).suffixes

    def __truediv__(self, other: str) -> RootHttpUrl:
        parsed = urlsplit(str(self))
        return RootHttpUrl(
            urlunsplit(
                (
                    parsed.scheme,
                    parsed.netloc,
                    f"{parsed.path.strip('/')}/{other.strip('/')}",
                    parsed.query,
                    parsed.fragment,
                )
            )
        )


class RootHttpUrl(_RootUrl[pydantic.HttpUrl]):
    """An untested HTTP URL, possibly a 'URL folder'"""

    root_model: ClassVar[type[RootModel[Any]]] = RootModel[pydantic.HttpUrl]
    _validated: pydantic.HttpUrl

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
            parent = current.parent
            if current == parent:
                break

            current = parent
            yield parent


class FtpUrl(_RootUrl[pydantic.FtpUrl]):
    """An untested FTP URL"""

    root_model: ClassVar[type[RootModel[Any]]] = RootModel[pydantic.FtpUrl]
    _validated: pydantic.FtpUrl

    @property
    def parent(self) -> FtpUrl:
        parsed = urlsplit(str(self))
        path = list(parsed.path.split("/"))[:-1]
        return FtpUrl(
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
    def parents(self) -> Iterable[FtpUrl]:
        """iterate over all URL parents (max 100)"""
        current = self
        for _ in range(100):
            parent = current.parent
            if current == parent:
                break

            current = parent
            yield parent
