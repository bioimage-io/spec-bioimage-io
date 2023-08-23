from contextlib import nullcontext
from typing import Any, ClassVar, Dict, Sequence, Type, Union
from unittest import TestCase

from annotated_types import Ge
from pydantic import ValidationError
from typing_extensions import Annotated

from bioimageio.spec._internal.base_nodes import ResourceDescriptionBase
from bioimageio.spec._internal.constants import ALERT, ERROR, INFO, WARNING, WARNING_LEVEL_CONTEXT_KEY
from bioimageio.spec._internal.warn import warn


class DummyNode(ResourceDescriptionBase):
    type: str = "generic"
    format_version: str = "0.1.0"
    a: Annotated[int, warn(Ge(0))] = 0
    b: Annotated[int, warn(Ge(0), WARNING)] = 0


class NestedDummyNode(ResourceDescriptionBase):
    type: str = "generic"
    format_version: str = "0.1.0"
    dummy: DummyNode


DUMMY_INPUT = {"a": -1, "b": -1}
NESTED_DICT_DUMMY_INPUT = dict(dummy=DUMMY_INPUT)
NESTED_NODE_DUMMY_INPUT = dict(dummy=DummyNode(a=-1, b=-1))


class Base:
    class TestWarnBase(TestCase):
        node_class: ClassVar[Type[Union[DummyNode, NestedDummyNode]]]
        raises: ClassVar[bool]
        inputs: ClassVar[Sequence[Dict[str, Any]]]

        def test(self):
            if self.raises:
                raises_ctxt = self.assertRaises(ValidationError)
            else:
                raises_ctxt = nullcontext()

            for ipt in self.inputs:
                with self.subTest(**ipt), raises_ctxt:
                    _ = self.node_class.model_validate(**ipt)


class TestWarnIgnores(Base.TestWarnBase):
    node_class = DummyNode
    raises = False
    inputs = (
        dict(obj=DUMMY_INPUT),
        dict(obj=DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ERROR}),
        dict(obj=DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ALERT}),
    )


class TestWarnIgnoresNested(Base.TestWarnBase):
    node_class = NestedDummyNode
    raises = False
    inputs = (
        dict(obj=NESTED_DICT_DUMMY_INPUT),
        dict(obj=NESTED_DICT_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ERROR}),
        dict(obj=NESTED_DICT_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ALERT}),
        dict(obj=NESTED_NODE_DUMMY_INPUT),
        dict(obj=NESTED_NODE_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ERROR}),
        dict(obj=NESTED_NODE_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ALERT}),
    )


class TestWarnRaises(Base.TestWarnBase):
    node_class = DummyNode
    raises = True
    inputs = (
        dict(obj=DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: WARNING}),
        dict(obj=DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: INFO}),
    )


class TestWarnRaisesNested(Base.TestWarnBase):
    node_class = NestedDummyNode
    raises = True
    inputs = (
        dict(obj=NESTED_DICT_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: WARNING}),
        dict(obj=NESTED_DICT_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: INFO}),
        dict(obj=NESTED_NODE_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: WARNING}),
        dict(obj=NESTED_NODE_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: INFO}),
    )
