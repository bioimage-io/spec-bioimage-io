from typing import Annotated
from unittest import TestCase

from annotated_types import Ge
from pydantic import ValidationError

from bioimageio.spec._internal._constants import ALERT, ERROR, INFO, WARNING, WARNING_LEVEL_CONTEXT_KEY
from bioimageio.spec._internal._warn import warn
from bioimageio.spec.shared.nodes import Node


class TestWarn(TestCase):
    class DummyNode(Node):
        a: Annotated[int, warn(Ge(0))] = 0
        b: Annotated[int, warn(Ge(0), WARNING)] = 0

    def test_warn_does_not_raise(self):
        _ = self.DummyNode.model_validate(dict(a=-1, b=-1))
        _ = self.DummyNode.model_validate(dict(a=-1, b=-1), context={WARNING_LEVEL_CONTEXT_KEY: ERROR})
        _ = self.DummyNode.model_validate(dict(a=-1, b=-1), context={WARNING_LEVEL_CONTEXT_KEY: ALERT})

    def test_warn_raises(self):
        with self.assertRaises(ValidationError):
            _ = self.DummyNode.model_validate(dict(a=-1, b=-1), context={WARNING_LEVEL_CONTEXT_KEY: WARNING})
        with self.assertRaises(ValidationError):
            _ = self.DummyNode.model_validate(dict(a=-1, b=-1), context={WARNING_LEVEL_CONTEXT_KEY: INFO})
