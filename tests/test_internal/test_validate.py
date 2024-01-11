from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError
from typing_extensions import Annotated

from bioimageio.spec._internal.types import FileSource
from bioimageio.spec._internal.types.field_validation import WithSuffix

NO_IO_CHECKS_CTXT = {"perform_io_checks": False}


def test_single_suffix():
    adapter = TypeAdapter(Annotated[FileSource, WithSuffix(".py", case_sensitive=True)])
    _ = adapter.validate_python(Path(__file__).name, context=dict(root=Path(__file__).parent))
    _ = adapter.validate_python("https://example.com/lala.py", context=NO_IO_CHECKS_CTXT)
    _ = adapter.validate_python("https://example.com/lala.py#section", context=NO_IO_CHECKS_CTXT)


def test_case_sensitive_suffix():
    adapter = TypeAdapter(Annotated[FileSource, WithSuffix(".py", case_sensitive=True)])
    with pytest.raises(ValidationError):
        _ = adapter.validate_python("https://example.com/lala.PY", context=NO_IO_CHECKS_CTXT)


def test_multiple_suffix():
    adapter = TypeAdapter(Annotated[FileSource, WithSuffix((".py", ".md"), case_sensitive=True)])
    _ = adapter.validate_python(Path(__file__).name, context=dict(root=Path(__file__).parent))
    _ = adapter.validate_python("https://example.com/lala.py", context=NO_IO_CHECKS_CTXT)
    _ = adapter.validate_python("https://example.com/lala.md#section", context=NO_IO_CHECKS_CTXT)


def test_wrong_usage():
    with pytest.raises(TypeError):
        _ = TypeAdapter(Annotated[int, WithSuffix(".py", case_sensitive=True)])
