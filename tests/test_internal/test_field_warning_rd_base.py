from typing import Any, Dict

import pytest
from annotated_types import Ge
from typing_extensions import Annotated

from bioimageio.spec._internal.base_nodes import ResourceDescriptionBase
from bioimageio.spec._internal.constants import ALERT, ERROR, INFO, WARNING, WARNING_LEVEL_CONTEXT_KEY
from bioimageio.spec._internal.field_warning import warn
from tests.utils import check_node


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


@pytest.mark.parametrize(
    "kwargs,valid",
    [
        (dict(obj=DUMMY_INPUT), True),
        (dict(obj=DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ERROR}), True),
        (dict(obj=DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ALERT}), True),
        (dict(obj=DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: WARNING}), False),
        (dict(obj=DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: INFO}), False),
    ],
)
def test_warn(kwargs: Dict[str, Any], valid: bool):
    check_node(DummyNode, kwargs, is_invalid=not valid)


@pytest.mark.parametrize(
    "kwargs,valid",
    [
        (dict(obj=NESTED_DICT_DUMMY_INPUT), True),
        (dict(obj=NESTED_DICT_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ERROR}), True),
        (dict(obj=NESTED_DICT_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ALERT}), True),
        (dict(obj=NESTED_NODE_DUMMY_INPUT), True),
        (dict(obj=NESTED_NODE_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ERROR}), True),
        (dict(obj=NESTED_NODE_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: ALERT}), True),
        (dict(obj=NESTED_DICT_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: WARNING}), False),
        (dict(obj=NESTED_DICT_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: INFO}), False),
        (dict(obj=NESTED_NODE_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: WARNING}), False),
        (dict(obj=NESTED_NODE_DUMMY_INPUT, context={WARNING_LEVEL_CONTEXT_KEY: INFO}), False),
    ],
)
def test_warn_nested(kwargs: Dict[str, Any], valid: bool):
    check_node(NestedDummyNode, kwargs, is_invalid=not valid)
