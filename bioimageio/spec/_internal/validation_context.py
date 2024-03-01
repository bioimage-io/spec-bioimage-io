from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal, Optional, Union

import pydantic
import requests.exceptions
from pydantic import DirectoryPath, TypeAdapter
from typing_extensions import Annotated

from bioimageio.spec._internal import settings
from bioimageio.spec._internal.base_nodes import ValidatedString
from bioimageio.spec._internal.field_validation import AfterValidator
from bioimageio.spec._internal.field_warning import issue_warning
from bioimageio.spec._internal.io_basics import BIOIMAGEIO_YAML, AbsoluteDirectory

WarningSeverity = Literal[20, 30, 35]
WarningLevel = Literal[WarningSeverity, 50]
"""With warning level x validation warnings of severity >=x are raised.
Highest warning level 50/error does not raise any validaiton warnings (only validation errors)."""
ERROR, ERROR_NAME = 50, "error"
"""A warning of the error level is always raised (equivalent to a validation error)"""

ALERT, ALERT_NAME = 35, "alert"
"""no ALERT nor ERROR -> RDF is worriless"""

WARNING, WARNING_NAME = 30, "warning"
"""no WARNING nor ALERT nor ERROR -> RDF is watertight"""

INFO, INFO_NAME = 20, "info"
"""info warnings are about purely cosmetic issues, etc."""


def validate_url_ok(url: str):
    if not validation_context_var.get().perform_io_checks:
        return url

    if url.startswith("https://colab.research.google.com/github/"):
        # head request for colab returns "Value error, 405: Method Not Allowed"
        # therefore we check if the source notebook exists at github instead
        val_url = url.replace(
            "https://colab.research.google.com/github/", "https://github.com/"
        )
    else:
        val_url = url

    try:
        response = requests.head(val_url)
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
        elif response.status_code in (301, 308):
            issue_warning(
                "URL redirected ({status_code}): consider updating {value} with new"
                " location: {location}",
                value=url,
                msg_context={
                    "status_code": response.status_code,
                    "location": response.headers.get("location"),
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

    return url


_http_url_adapter = TypeAdapter(pydantic.HttpUrl)  # pyright: ignore[reportCallIssue]


class HttpUrl(
    ValidatedString[
        Annotated[
            str,
            AfterValidator(lambda value: str(_http_url_adapter.validate_python(value))),
            AfterValidator(validate_url_ok),
        ]
    ]
):
    @property
    def scheme(self) -> str:
        return pydantic.AnyUrl(str(self)).scheme

    @property
    def host(self) -> Optional[str]:
        return pydantic.AnyUrl(str(self)).host

    @property
    def path(self) -> Optional[str]:
        return pydantic.AnyUrl(str(self)).path


@dataclass(frozen=True)
class ValidationContext:
    _context_tokens: "List[Token[ValidationContext]]" = field(
        init=False, default_factory=list
    )

    root: Union[HttpUrl, AbsoluteDirectory] = Path()
    """url/directory serving as base to resolve any relative file paths"""

    warning_level: WarningLevel = 50
    """raise warnings of severity s as validation errors if s >= `warning_level`"""

    file_name: str = BIOIMAGEIO_YAML
    """file name of the bioimageio Yaml file"""

    perform_io_checks: bool = settings.perform_io_checks
    """wether or not to perfrom validation that requires IO operations like download or reading a file from disk"""

    def replace(
        self,
        root: Optional[Union[DirectoryPath, HttpUrl]] = None,
        warning_level: Optional[WarningLevel] = None,
        file_name: Optional[str] = None,
        perform_io_checks: Optional[bool] = None,
    ) -> "ValidationContext":
        return ValidationContext(
            root=self.root if root is None else root,
            warning_level=(
                self.warning_level if warning_level is None else warning_level
            ),
            file_name=self.file_name if file_name is None else file_name,
            perform_io_checks=(
                self.perform_io_checks
                if perform_io_checks is None
                else perform_io_checks
            ),
        )

    def __enter__(self):
        self._context_tokens.append(validation_context_var.set(self))
        return self

    def __exit__(self, type, value, traceback):  # type: ignore
        validation_context_var.reset(self._context_tokens.pop(-1))


validation_context_var: ContextVar[ValidationContext] = ContextVar(
    "validation_context_var", default=ValidationContext()
)
