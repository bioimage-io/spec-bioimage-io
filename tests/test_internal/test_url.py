from typing import Type

import pytest
import requests.exceptions
from requests_mock import Mocker as RequestsMocker

from bioimageio.spec._internal.validation_context import ValidationContext


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "https://colab.research.google.com/github/bioimage-io/spec-bioimage-io/blob/main/example/load_model_and_create_your_own.ipynb",
        "https://www.kaggle.com/c/data-science-bowl-2018",
    ],
)
def test_httpurl_valid(url: str):
    from bioimageio.spec._internal.url import HttpUrl

    with ValidationContext(perform_io_checks=True):
        assert HttpUrl(url).exists(), url


@pytest.mark.parametrize(
    "text,status_code",
    [
        ("OK", 200),
        ("found", 302),
        ("redirected", 301),
        ("redirected", 303),
        ("redirected", 308),
        ("let's ignore this I guess??", 405),
    ],
)
def test_httpurl_mock_valid(text: str, status_code: int, requests_mock: RequestsMocker):
    from bioimageio.spec._internal.url import HttpUrl

    url = "https://mock_example.com"
    _ = requests_mock.get(url, text=text, status_code=status_code)
    assert HttpUrl(url).exists()


@pytest.mark.parametrize(
    "text,status_code",
    [
        ("forbidden", 403),
        ("Not found", 404),
        ("just wrong", 199),
    ],
)
def test_httpurl_mock_invalid(
    text: str, status_code: int, requests_mock: RequestsMocker
):
    from bioimageio.spec._internal.url import HttpUrl

    url = "https://mock_example.com"
    _ = requests_mock.head(url, text=text, status_code=status_code)
    _ = requests_mock.get(url, text=text, status_code=status_code)
    with ValidationContext(perform_io_checks=True):
        with pytest.raises(ValueError):
            _ = HttpUrl(url)

    with ValidationContext(perform_io_checks=False):
        assert not HttpUrl(url).exists()


@pytest.mark.parametrize(
    "exc",
    [
        requests.exceptions.InvalidURL,
    ],
)
def test_httpurl_mock_exc(exc: Type[Exception], requests_mock: RequestsMocker):
    from bioimageio.spec._internal.url import HttpUrl

    url = "https://mock_example.com"
    _ = requests_mock.head(url, exc=exc)
    with ValidationContext(perform_io_checks=True):
        with pytest.raises(ValueError):
            _ = HttpUrl(url)

    with ValidationContext(perform_io_checks=False):
        assert not HttpUrl(url).exists()


@pytest.mark.parametrize(
    "url,io_check",
    [
        ("https://example.invalid", True),
        ("https://example.invalid", False),
    ],
)
def test_httpurl_nonexisting(url: str, io_check: bool):
    from bioimageio.spec._internal.url import HttpUrl

    with ValidationContext(perform_io_checks=io_check):
        assert HttpUrl(url).exists(), url


@pytest.mark.parametrize(
    "url",
    [
        "invalid-url",
    ],
)
def test_httpurl_invalid(url: str):
    from bioimageio.spec._internal.url import HttpUrl

    with pytest.raises(ValueError), ValidationContext(perform_io_checks=False):
        _ = HttpUrl(url)
