import requests
import requests.exceptions
from pydantic import model_validator

from .field_warning import issue_warning
from .root_url import RootHttpUrl
from .validation_context import validation_context_var


def check_url(url: str) -> None:
    if url.startswith("https://colab.research.google.com/github/"):
        # head request for colab returns "Value error, 405: Method Not Allowed"
        # therefore we check if the source notebook exists at github instead
        val_url = url.replace(
            "https://colab.research.google.com/github/", "https://github.com/"
        )
    else:
        val_url = url

    try:
        response = requests.head(val_url, timeout=(3, 3))
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
        follow_up_with_get = False
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
            follow_up_with_get = True
            issue_warning(
                "{status_code}: {reason} {value}",
                value=url,
                msg_context={
                    "status_code": response.status_code,
                    "reason": response.reason,
                },
            )
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

        if follow_up_with_get:
            pass
            # TODO follow up forbidden head request with get
            # motivating example: 403: Forbidden https://elifesciences.org/articles/57613


class HttpUrl(RootHttpUrl, frozen=True):
    @model_validator(mode="after")
    def _check_url(self):
        if not validation_context_var.get().perform_io_checks:
            return self

        check_url(str(self))
        return self
