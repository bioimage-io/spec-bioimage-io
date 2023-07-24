from pathlib import Path
from typing import Annotated
from unittest import TestCase

from pydantic import TypeAdapter, ValidationError

from bioimageio.spec._internal._validate import WithSuffix
from bioimageio.spec.shared.types import FileSource


class TestWithSuffix(TestCase):
    def test_single_suffix(self):
        adapter = TypeAdapter(Annotated[FileSource, WithSuffix(".py", case_sensitive=True)])
        adapter.validate_python(__file__, context=dict(root=Path(__file__).parent))
        adapter.validate_python("https://example.com/lala.py")
        adapter.validate_python("https://example.com/lala.py#section")

    def test_case_sensitive_suffix(self):
        adapter = TypeAdapter(Annotated[FileSource, WithSuffix(".py", case_sensitive=True)])
        with self.assertRaises(ValidationError):
            adapter.validate_python("https://example.com/lala.PY")

    def test_multiple_suffix(self):
        adapter = TypeAdapter(Annotated[FileSource, WithSuffix([".py", ".md"], case_sensitive=True)])
        adapter.validate_python(__file__, context=dict(root=Path(__file__).parent))
        adapter.validate_python("https://example.com/lala.py")
        adapter.validate_python("https://example.com/lala.md#section")

    def test_wrong_usage(self):
        with self.assertRaises(TypeError):
            TypeAdapter(Annotated[int, WithSuffix(".py", case_sensitive=True)])
