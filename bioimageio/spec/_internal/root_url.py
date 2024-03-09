from __future__ import annotations

from typing import Optional
from urllib.parse import urlsplit, urlunsplit

import pydantic
from pydantic import AfterValidator, TypeAdapter
from typing_extensions import Annotated

from .validated_string import ValidatedString

_http_url_adapter = TypeAdapter(pydantic.HttpUrl)  # pyright: ignore[reportCallIssue]


class RootHttpUrl(
    ValidatedString[
        Annotated[
            str,
            AfterValidator(lambda value: str(_http_url_adapter.validate_python(value))),
        ]
    ],
    frozen=True,
):
    """A 'URL folder', possibly an invalid http URL"""

    @property
    def _url(self):
        return pydantic.AnyUrl(str(self))

    @property
    def scheme(self) -> str:
        return self._url.scheme

    @property
    def host(self) -> Optional[str]:
        return self._url.host

    @property
    def path(self) -> Optional[str]:
        return self._url.path

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
