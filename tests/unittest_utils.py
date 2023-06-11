from __future__ import annotations
from pathlib import Path
from typing import Any, Callable, Optional
from unittest import TestCase

from pydantic import ValidationError

from bioimageio.spec.shared.nodes import Node


class BaseTestCases:
    """class to hide base test cases to not discover them as tests"""

    class TestNode(TestCase):
        """template to test any Node subclass with valid and invalid kwargs"""

        NodeClass: type[Node]
        valid_kwargs: list[dict[str, Any]]
        invalid_kwargs: list[dict[str, Any]]
        context: Optional[dict[str, Any]] = dict(root=Path(__file__).parent)

        # tests added by __init_subclass__ depending on class attributes
        test_valid: Optional[Callable[[BaseTestCases.TestNode], None]] = None
        test_invalid: Optional[Callable[[BaseTestCases.TestNode], None]] = None

        def __init_subclass__(cls, /, **kwargs: Any):
            super().__init_subclass__(**kwargs)
            assert hasattr(cls, "NodeClass")
            assert any(hasattr(cls, t) for t in ["valid_kwargs", "invalid_kwargs", "invalid_type_kwargs"])
            if hasattr(cls, "valid_kwargs"):
                cls.test_valid = cls._test_valid

            if hasattr(cls, "invalid_kwargs"):
                cls.test_invalid = cls._test_invalid

        def _test_valid(self):
            for kw in self.valid_kwargs:
                with self.subTest(**kw):
                    try:
                        self.NodeClass.model_validate(kw, context=self.context)
                    except ValidationError as e:
                        self.fail(e)

        def _test_invalid(self):
            for kw in self.invalid_kwargs:
                with self.subTest(**kw):
                    self.assertRaises(ValidationError, self.NodeClass.model_validate, kw, context=self.context)
