from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError
from typing_extensions import Annotated

from bioimageio.spec._internal.field_validation import WithSuffix
from bioimageio.spec.types import FileSource


def test_single_suffix():
    adapter = TypeAdapter(Annotated[FileSource, WithSuffix(".py", case_sensitive=True)])
    _ = adapter.validate_python(Path(__file__).name, context=dict(root=Path(__file__).parent))
    _ = adapter.validate_python("https://example.com/lala.py")
    _ = adapter.validate_python("https://example.com/lala.py#section")


def test_case_sensitive_suffix():
    adapter = TypeAdapter(Annotated[FileSource, WithSuffix(".py", case_sensitive=True)])
    with pytest.raises(ValidationError):
        _ = adapter.validate_python("https://example.com/lala.PY")


def test_multiple_suffix():
    adapter = TypeAdapter(Annotated[FileSource, WithSuffix([".py", ".md"], case_sensitive=True)])
    _ = adapter.validate_python(Path(__file__).name, context=dict(root=Path(__file__).parent))
    _ = adapter.validate_python("https://example.com/lala.py")
    _ = adapter.validate_python("https://example.com/lala.md#section")


def test_wrong_usage():
    with pytest.raises(TypeError):
        _ = TypeAdapter(Annotated[int, WithSuffix(".py", case_sensitive=True)])
