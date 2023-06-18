from __future__ import annotations
from pathlib import Path
from typing import Any, Callable, Literal, Optional, Sequence
from unittest import TestCase

from pydantic import ValidationError
import bioimageio.spec
from bioimageio.spec.shared.nodes import Node

from ruamel.yaml import YAML

yaml = YAML(typ="safe")


class BaseTestCases:
    """class to hide base test cases to not discover them as tests"""

    class TestNode(TestCase):
        """template to test any Node subclass with valid and invalid kwargs"""

        NodeClass: type[Node]
        valid_kwargs: Sequence[dict[str, Any]]
        valid_test_names: Optional[Sequence[str]] = None
        invalid_kwargs: Sequence[dict[str, Any]]
        invalid_test_names: Optional[Sequence[str]] = None
        context: Optional[dict[str, Any]] = dict(root=Path(__file__).parent)

        def test_valid(self):
            for kw, stkw in self._iterate_over(self.valid_kwargs, self.valid_test_names):
                with self.subTest(**stkw):
                    try:
                        self.NodeClass.model_validate(kw, context=self.context)
                    except ValidationError as e:
                        self.fail(e)

        def test_invalid(self):
            for kw, stkw in self._iterate_over(self.invalid_kwargs, self.invalid_test_names):
                with self.subTest(**stkw):
                    self.assertRaises(ValidationError, self.NodeClass.model_validate, kw, context=self.context)

        @staticmethod
        def _iterate_over(kwargs_seq: Sequence[dict[str, Any]], names: Optional[Sequence[str]]):
            if names is None:
                sub_test_kwargs = kwargs_seq
            else:
                sub_test_kwargs = [dict(msg=n) for n in names]

            assert len(kwargs_seq) == len(sub_test_kwargs)
            for kw, stkw in zip(kwargs_seq, sub_test_kwargs):
                yield kw, stkw

    class TestResourceDescriptionExampleSpecs(TestNode):
        test_invalid = None  # type: ignore  # remove test_invalid to not inflate test count
        context = None
        invalid_kwargs = ()

        def __init__(self, methodName: str = "runTest") -> None:
            typ = self.__class__.__name__[4:].lower()
            self.NodeClass = getattr(getattr(bioimageio.spec, typ), typ.capitalize())
            root = Path(__file__).parent / "../example_specs" / (typ + "s")
            self.valid_kwargs = []
            self.valid_test_names = []
            for folder in root.iterdir():
                with (folder / "rdf.yaml").open(encoding="utf-8") as f:
                    data: dict[str, Any] = yaml.load(f)
                    assert isinstance(data, dict)
                    assert all(isinstance(k, str) for k in data)
                    data["root"] = folder
                    self.valid_kwargs.append(data)
                    self.valid_test_names.append(str(folder.relative_to(root)))

            super().__init__(methodName)
