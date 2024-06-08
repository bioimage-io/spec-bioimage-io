from typing import Any, ClassVar, Optional, Type, Union

import pydantic
import requests
import requests.exceptions
from loguru import logger
from pydantic import RootModel, model_validator
from typing_extensions import Literal, assert_never

from .field_warning import issue_warning
from .root_url import RootHttpUrl
from .validation_context import validation_context_var


def _validate_url(url: Union[str, pydantic.HttpUrl]) -> pydantic.AnyUrl:
    return _validate_url_impl(url, request_mode="head")


def _validate_url_impl(
    url: Union[str, pydantic.HttpUrl],
    request_mode: Literal["head", "get_stream", "get"],
    timeout: int = 3,
) -> pydantic.AnyUrl:

    url = str(url)
    val_url = url

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
        )

    try:
        if request_mode == "head":
            response = requests.head(val_url, timeout=timeout)
        elif request_mode == "get_stream":
            response = requests.get(val_url, stream=True, timeout=timeout)
        elif request_mode == "get":
            response = requests.get(val_url, stream=False, timeout=timeout)
        else:
            assert_never(request_mode)
    except (
        requests.exceptions.ChunkedEncodingError,
        requests.exceptions.ContentDecodingError,
        requests.exceptions.InvalidHeader,
        requests.exceptions.InvalidJSONError,
        requests.exceptions.InvalidSchema,
        requests.exceptions.InvalidURL,
        requests.exceptions.MissingSchema,
        requests.exceptions.StreamConsumedError,
        requests.exceptions.TooManyRedirects,
        requests.exceptions.UnrewindableBodyError,
        requests.exceptions.URLRequired,
    ) as e:
        raise ValueError(
            f"Invalid URL '{url}': {e}\nrequest: {e.request}\nresponse: {e.response}"
        )
    except requests.RequestException as e:
        issue_warning(
            "Failed to validate URL '{value}': {error}\nrequest: {request}\nresponse: {response}",
            value=url,
            msg_context={"error": str(e), "response": e.response, "request": e.request},
        )
    except Exception as e:
        issue_warning(
            "Failed to validate URL '{value}': {error}",
            value=url,
            msg_context={"error": str(e)},
        )
    else:
        if response.status_code == 302:  # found
            pass
        elif response.status_code in (301, 303, 308):
            issue_warning(
                "URL redirected ({status_code}): consider updating {value} with new"
                + " location: {location}",
                value=url,
                msg_context={
                    "status_code": response.status_code,
                    "location": response.headers.get("location"),
                },
            )
        elif response.status_code == 403:  # forbidden
            if request_mode == "head":
                return _validate_url_impl(
                    url, request_mode="get_stream", timeout=timeout
                )
            elif request_mode == "get_stream":
                return _validate_url_impl(url, request_mode="get", timeout=timeout)
            elif request_mode == "get":
                raise ValueError(f"{response.status_code}: {response.reason} {url}")
            else:
                assert_never(request_mode)
        elif response.status_code == 405:
            issue_warning(
                "{status_code}: {reason} {value}",
                value=url,
                msg_context={
                    "status_code": response.status_code,
                    "reason": response.reason,
                },
            )
        elif response.status_code != 200:
            raise ValueError(f"{response.status_code}: {response.reason} {url}")

    return pydantic.AnyUrl(url)


class HttpUrl(RootHttpUrl):
    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[pydantic.HttpUrl]
    _exists: Optional[bool] = None

    @model_validator(mode="after")
    def _validate_url(self):
        url = self._validated
        context = validation_context_var.get()
        if context.perform_io_checks and str(url) not in context.known_files:
            self._validated = _validate_url(url)
            self._exists = True

        return self

    def exists(self):
        """True if URL is available"""
        if self._exists is None:
            try:
                self._validated = _validate_url(self._validated)
            except Exception as e:
                logger.info(e)
                self._exists = False
            else:
                self._exists = True

        return self._exists
