from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError
from typing_extensions import Annotated

from bioimageio.spec._internal.io import WithSuffix
from bioimageio.spec._internal.types import FileSource
from bioimageio.spec._internal.validation_context import ValidationContext


def test_single_suffix():
    adapter: TypeAdapter[FileSource] = TypeAdapter(
        Annotated[FileSource, WithSuffix(".py", case_sensitive=True)]
    )
    with ValidationContext(root=Path(__file__).parent):
        _ = adapter.validate_python(Path(__file__).name)

    with ValidationContext(perform_io_checks=False):
        _ = adapter.validate_python("https://example.com/lala.py")
        _ = adapter.validate_python("https://example.com/lala.py#section")


def test_case_sensitive_suffix():
    adapter: TypeAdapter[FileSource] = TypeAdapter(
        Annotated[FileSource, WithSuffix(".py", case_sensitive=True)]
    )
    with ValidationContext(perform_io_checks=False), pytest.raises(ValidationError):
        _ = adapter.validate_python("https://example.com/lala.PY")


def test_multiple_suffix():
    adapter: TypeAdapter[FileSource] = TypeAdapter(
        Annotated[FileSource, WithSuffix((".py", ".md"), case_sensitive=True)]
    )
    with ValidationContext(root=Path(__file__).parent):
        _ = adapter.validate_python(Path(__file__).name)

    with ValidationContext(perform_io_checks=False):
        _ = adapter.validate_python("https://example.com/lala.py")
        _ = adapter.validate_python("https://example.com/lala.md#section")
