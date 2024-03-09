from typing import Any, Dict

import pytest
from annotated_types import Ge
from typing_extensions import Annotated

from bioimageio.spec._internal.common_nodes import Node
from bioimageio.spec._internal.field_warning import warn
from bioimageio.spec._internal.validation_context import ValidationContext
from bioimageio.spec._internal.warning_levels import (
    ALERT,
    ERROR,
    INFO,
    WARNING,
)
from tests.utils import WARNING_LEVEL_CONTEXT_KEY, check_node


class DummyNode(Node):
    a: Annotated[int, warn(Ge(0), "smaller than zero")] = 0
    b: Annotated[int, warn(Ge(0), "smaller than zero", WARNING)] = 0


class NestedDummyNode(Node):
    dummy: DummyNode


DUMMY_INPUT: Dict[str, Any] = {"a": -1, "b": -1}
NESTED_DICT_DUMMY_INPUT = dict(dummy=DUMMY_INPUT)
NESTED_NODE_DUMMY_INPUT = dict(dummy=DummyNode(**DUMMY_INPUT))


@pytest.mark.parametrize(
    "kwargs,context,valid",
    [
        (DUMMY_INPUT, {}, True),
        (DUMMY_INPUT, {WARNING_LEVEL_CONTEXT_KEY: ERROR}, True),
        (DUMMY_INPUT, {WARNING_LEVEL_CONTEXT_KEY: ALERT}, True),
        (DUMMY_INPUT, {WARNING_LEVEL_CONTEXT_KEY: WARNING}, False),
        (DUMMY_INPUT, {WARNING_LEVEL_CONTEXT_KEY: INFO}, False),
    ],
)
def test_warn(kwargs: Dict[str, Any], context: ValidationContext, valid: bool):
    check_node(DummyNode, kwargs, context=context, is_invalid=not valid)


@pytest.mark.parametrize(
    "kwargs,context,valid",
    [
        (NESTED_DICT_DUMMY_INPUT, {}, True),
        (NESTED_DICT_DUMMY_INPUT, {WARNING_LEVEL_CONTEXT_KEY: ERROR}, True),
        (NESTED_DICT_DUMMY_INPUT, {WARNING_LEVEL_CONTEXT_KEY: ALERT}, True),
        (NESTED_NODE_DUMMY_INPUT, {}, True),
        (NESTED_NODE_DUMMY_INPUT, {WARNING_LEVEL_CONTEXT_KEY: ERROR}, True),
        (NESTED_NODE_DUMMY_INPUT, {WARNING_LEVEL_CONTEXT_KEY: ALERT}, True),
        (NESTED_DICT_DUMMY_INPUT, {WARNING_LEVEL_CONTEXT_KEY: WARNING}, False),
        (NESTED_DICT_DUMMY_INPUT, {WARNING_LEVEL_CONTEXT_KEY: INFO}, False),
        (
            NESTED_NODE_DUMMY_INPUT,
            {WARNING_LEVEL_CONTEXT_KEY: WARNING},
            True,  # no reevaluation of node instance
        ),
        (
            NESTED_NODE_DUMMY_INPUT,
            {WARNING_LEVEL_CONTEXT_KEY: INFO},
            True,  # no reevaluation of node instance
        ),
    ],
)
def test_warn_nested(kwargs: Dict[str, Any], context: ValidationContext, valid: bool):
    check_node(NestedDummyNode, kwargs, context=context, is_invalid=not valid)
