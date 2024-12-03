import pytest


@pytest.mark.parametrize("url", ["https://github.com"])
def test_httpurl(url: str):
    from bioimageio.spec._internal.url import HttpUrl

    assert HttpUrl(url).exists(), url
