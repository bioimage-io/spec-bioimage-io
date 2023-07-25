from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional, Sequence, Type
from unittest import TestCase

from pydantic import TypeAdapter, ValidationError

from bioimageio.spec.shared.nodes import Node
from bioimageio.spec.shared.validation import ValidationContext


@dataclass
class SubTest(ABC):
    kwargs: Dict[str, Any]
    name: Optional[str] = None
    context: Optional[ValidationContext] = None
    node_class: Optional[Type[Node]] = None

    def __post_init__(self):
        if self.__class__ == SubTest:
            raise TypeError("Cannot instantiate abstract class.")


@dataclass
class Valid(SubTest):
    expected_dump_raw: Optional[Dict[str, Any]] = None
    expected_dump_python: Optional[Dict[str, Any]] = None


@dataclass
class Invalid(SubTest):
    expect: Type[Exception] = ValidationError


class BaseTestCases:
    """class to hide base test cases to not discover them as tests"""

    class TestNode(TestCase):
        """template to test any Node subclass with valid and invalid kwargs"""

        default_node_class: Type[Node]
        default_context: ValidationContext = ValidationContext(root=Path(__file__).parent)

        sub_tests: Sequence[SubTest]
        allow_empty: bool = False

        def test_valid(self):
            for st in self.sub_tests:
                if isinstance(st, Invalid):
                    continue

                assert isinstance(st, Valid)
                with self.subTest(**self.get_subtest_kwargs(st)):
                    nc = self.get_node_class(st)
                    node = nc.model_validate(st.kwargs, context=self.get_context(st))
                    for mode, expected in [
                        ("python", st.expected_dump_python),
                        ("json", st.expected_dump_raw),
                    ]:
                        with self.subTest(_dump_mode=mode):
                            actual = node.model_dump(mode=mode, round_trip=True)
                            assert expected is None or actual == expected, (actual, expected)

        def test_invalid(self):
            for st in self.sub_tests:
                if isinstance(st, Valid):
                    continue

                assert isinstance(st, Invalid)
                with self.subTest(**self.get_subtest_kwargs(st)):
                    nc = self.get_node_class(st)
                    self.assertRaises(st.expect, nc.model_validate, st.kwargs, context=self.get_context(st))

        def test_empty(self):
            """assure that emtpy input data raises a validation error, not a KeyError, AttributeError, etc."""
            if not hasattr(self, "default_node_class"):
                self.skipTest("no default node class specified")

            nc = self.default_node_class
            if self.allow_empty:
                nc.model_validate({})
            else:
                self.assertRaises(ValidationError, nc.model_validate, {})

        def get_context(self, st: SubTest) -> Dict[str, Any]:
            if st.context is None:
                return dict(self.default_context)
            else:
                return dict(st.context)

        def get_node_class(self, st: SubTest) -> Type[Node]:
            return st.node_class or self.default_node_class

        @staticmethod
        def get_subtest_kwargs(st: SubTest) -> Dict[str, Any]:
            if st.name is not None:
                return dict(name=st.name)
            else:
                ret = dict(st.kwargs)
                if st.context is not None:
                    ret["context"] = st.context

                return ret

    class TestType(TestCase):
        type_: ClassVar[Type[Any]]
        valid: Sequence[Any]
        invalid: Sequence[Any]
        type_adapter: TypeAdapter[Any]

        def setUp(self) -> None:
            self.type_adapter = TypeAdapter(self.type_)
            return super().setUp()

        def test_valid(self):
            for v in self.valid:
                with self.subTest(v=v):
                    try:
                        self.type_adapter.validate_python(v)
                    except Exception as e:
                        self.fail(str(e))

        def test_invalid(self):
            for v in self.invalid:
                with self.subTest(iv=v):
                    self.assertRaises(ValidationError, self.type_adapter.validate_python, v)
