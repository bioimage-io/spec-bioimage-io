from pathlib import Path
from unittest import TestCase

from pydantic import TypeAdapter, ValidationError
from typing_extensions import Annotated

from bioimageio.spec._internal._validate import WithSuffix
from bioimageio.spec.types import FileSource


class TestWithSuffix(TestCase):
    def test_single_suffix(self):
        adapter = TypeAdapter(Annotated[FileSource, WithSuffix(".py", case_sensitive=True)])
        _ = adapter.validate_python(__file__, context=dict(root=Path(__file__).parent))
        _ = adapter.validate_python("https://example.com/lala.py")
        _ = adapter.validate_python("https://example.com/lala.py#section")

    def test_case_sensitive_suffix(self):
        adapter = TypeAdapter(Annotated[FileSource, WithSuffix(".py", case_sensitive=True)])
        with self.assertRaises(ValidationError):
            _ = adapter.validate_python("https://example.com/lala.PY")

    def test_multiple_suffix(self):
        adapter = TypeAdapter(Annotated[FileSource, WithSuffix([".py", ".md"], case_sensitive=True)])
        _ = adapter.validate_python(__file__, context=dict(root=Path(__file__).parent))
        _ = adapter.validate_python("https://example.com/lala.py")
        _ = adapter.validate_python("https://example.com/lala.md#section")

    def test_wrong_usage(self):
        with self.assertRaises(TypeError):
            _ = TypeAdapter(Annotated[int, WithSuffix(".py", case_sensitive=True)])
