import ast
import sys
import warnings
from typing import Literal
from urllib.parse import urlparse


def get_ref_url(
    type_: Literal["class", "function"], name: str, github_file_url: str
) -> str:
    """get github url with line range fragment to reference implementation from non-raw github file url

    example:
    >>> get_ref_url(
    ...     "class",
    ...     "Binarize",
    ...     "https://github.com/bioimage-io/core-bioimage-io-python/blob/main/bioimageio/core/prediction_pipeline/_processing.py"
    ... )
    'https://github.com/bioimage-io/core-bioimage-io-python/blob/main/bioimageio/core/prediction_pipeline/_processing.py#L120-L127'
    """
    # hotfix to handle requests not available in pyodide, see
    # https://github.com/bioimage-io/bioimage.io/issues/216#issuecomment-1012422194
    try:
        import requests  # not available in pyodide
    except Exception:
        warnings.warn(
            f"Could not reslove {github_file_url} because requests library is not"
            + " available."
        )
        return "URL NOT RESOLVED"

    assert not urlparse(github_file_url).fragment, "unexpected url fragment"
    look_for = {"class": ast.ClassDef, "function": ast.FunctionDef}[type_]
    raw_github_file_url = github_file_url.replace(
        "github.com", "raw.githubusercontent.com"
    ).replace("/blob/", "/")
    try:
        code = requests.get(raw_github_file_url).text
    except requests.RequestException as e:
        warnings.warn(
            f"Could not resolve {github_file_url} due to {e}. Please check your"
            + " internet connection."
        )
        return "URL NOT RESOLVED"
    tree = ast.parse(code)

    for d in tree.body:
        if isinstance(d, look_for):
            assert hasattr(d, "name")
            if d.name == name:
                assert hasattr(d, "decorator_list")
                start = d.decorator_list[0].lineno if d.decorator_list else d.lineno
                if sys.version_info >= (3, 8):
                    stop = d.end_lineno
                else:
                    stop = d.lineno + 1
                break
    else:
        raise ValueError(f"{type_} {name} not found in {github_file_url}")

    return f"{github_file_url}#L{start}-L{stop}"
