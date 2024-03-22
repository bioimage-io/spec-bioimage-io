from pathlib import PurePath
from typing import Any

import pytest
from pydantic import ValidationError

from bioimageio.spec._internal.validation_context import ValidationContext


@pytest.mark.parametrize("p", [PurePath("maybe_a_file"), "maybe_a_file"])
def test_valid_relative_file_path(p: Any):
    from bioimageio.spec._internal.io import RelativeFilePath

    with ValidationContext(perform_io_checks=False):
        _ = RelativeFilePath(p)


@pytest.mark.parametrize(
    "p",
    [
        PurePath(),
        PurePath(""),
        PurePath("."),
        PurePath("http://example.cm"),
        PurePath("https://example.com"),
    ],
)
def test_invalid_relative_file_path(p: Any):
    from bioimageio.spec._internal.io import RelativeFilePath

    with ValidationContext(perform_io_checks=False), pytest.raises(ValidationError):
        _ = RelativeFilePath(p)


@pytest.mark.parametrize(
    "p",
    [
        PurePath(__file__).parent,
    ],
)
def test_invalid_relative_file_path_io_check(p: Any):
    from bioimageio.spec._internal.io import RelativeFilePath

    with ValidationContext(perform_io_checks=True), pytest.raises(ValidationError):
        _ = RelativeFilePath(p)
