from contextlib import nullcontext
from typing import Any, ClassVar, Optional, Type, Union

import httpx
import pydantic
from loguru import logger
from pydantic import RootModel
from typing_extensions import Literal, assert_never

from . import warning_levels
from ._settings import settings
from .field_warning import issue_warning
from .root_url import RootHttpUrl
from .validation_context import get_validation_context


def _validate_url(url: Union[str, pydantic.HttpUrl]) -> pydantic.HttpUrl:
    return _validate_url_impl(url, request_mode="head", timeout=settings.http_timeout)


_KNOWN_VALID_URLS = ("https://zenodo.org/records/3446812/files/unet2d_weights.torch",)
"""known valid urls to bypass validation for to avoid sporadic 503 errors in tests etc."""


def _validate_url_impl(
    url: Union[str, pydantic.HttpUrl],
    request_mode: Literal["head", "get_stream", "get"],
    timeout: float,
) -> pydantic.HttpUrl:
    url = str(url)
    context = get_validation_context()
    if url in context.known_files:
        return pydantic.HttpUrl(url)

    val_url = url

    if (
        url.startswith("http://example.com")
        or url.startswith("https://example.com")
        or url in _KNOWN_VALID_URLS
    ):
        return pydantic.HttpUrl(url)

    if url.startswith("https://colab.research.google.com/github/"):
        # get requests for colab returns 200 even if the source notebook does not exists.
        # We therefore validate the url to the notebbok instead (for github notebooks)
        val_url = url.replace(
            "https://colab.research.google.com/github/", "https://github.com/"
        )
    elif url.startswith("https://colab.research.google.com/"):
        # TODO: improve validation of non-github colab urls
        issue_warning(
            "colab urls currently pass even if the notebook url was not found. Cannot fully validate {value}",
            value=url,
            severity=warning_levels.INFO,
        )

    try:
        if request_mode in ("head", "get"):
            request_ctxt = nullcontext(
                httpx.request(
                    request_mode.upper(),
                    val_url,
                    timeout=timeout,
                    follow_redirects=True,
                )
            )
        elif request_mode == "get_stream":
            request_ctxt = httpx.stream(
                "GET", val_url, timeout=timeout, follow_redirects=True
            )
        else:
            assert_never(request_mode)

        with request_ctxt as r:
            status_code = r.status_code
            reason = r.reason_phrase
            location = r.headers.get("location")

    except (
        httpx.InvalidURL,
        httpx.TooManyRedirects,
    ) as e:
        raise ValueError(f"Invalid URL '{url}': {e}")
    except httpx.RequestError as e:
        issue_warning(
            "Failed to validate URL '{value}': {error}\nrequest: {request}",
            value=url,
            msg_context={"error": str(e), "request": e.request},
        )
    except Exception as e:
        issue_warning(
            "Failed to validate URL '{value}': {error}",
            value=url,
            msg_context={"error": str(e)},
        )
    else:
        if status_code == 200:  # ok
            pass
        elif status_code in (302, 303):  # found
            pass
        elif status_code in (301, 308):
            issue_warning(
                "URL redirected ({status_code}): consider updating {value} with new"
                + " location: {location}",
                value=url,
                severity=warning_levels.INFO,
                msg_context={
                    "status_code": status_code,
                    "location": location,
                },
            )
        elif request_mode == "head":
            return _validate_url_impl(url, request_mode="get_stream", timeout=timeout)
        elif request_mode == "get_stream":
            return _validate_url_impl(url, request_mode="get", timeout=timeout)
        elif request_mode == "get":
            issue_warning(
                "{status_code}: {reason} ({value})",
                value=url,
                severity=(
                    warning_levels.INFO
                    if status_code == 405  # may be returned due to a captcha
                    else warning_levels.WARNING
                ),
                msg_context={
                    "status_code": status_code,
                    "reason": reason,
                },
            )
        else:
            assert_never(request_mode)

    context.known_files[url] = None
    return pydantic.HttpUrl(url)


class HttpUrl(RootHttpUrl):
    """A URL with the HTTP or HTTPS scheme."""

    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[pydantic.HttpUrl]
    _exists: Optional[bool] = None

    def _after_validator(self):
        self = super()._after_validator()
        context = get_validation_context()
        if context.perform_io_checks:
            _ = self.exists()

        return self

    def exists(self):
        """True if URL is available"""
        if self._exists is None:
            ctxt = get_validation_context()
            try:
                with ctxt.replace(warning_level=warning_levels.WARNING):
                    self._validated = _validate_url(self._validated)
            except Exception as e:
                if ctxt.log_warnings:
                    logger.info(e)

                self._exists = False
            else:
                self._exists = True

        return self._exists
