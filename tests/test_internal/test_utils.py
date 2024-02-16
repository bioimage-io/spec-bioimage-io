from contextlib import nullcontext
from typing import Any, Dict, Tuple

import pytest


@pytest.mark.parametrize(
    "args,kwargs,valid",
    [
        ((1, 1, 1, 1, 1), dict(c1=1, c2=1, d=1), True),
        ((1, 1, 1, 1, 1), dict(c1=1, c2=1), True),
        ((1, 1, 1, 1), dict(c1=1, c2=1, d=1), True),
        ((1, 1, 1, 1), dict(c1=1, c2=1), True),
        ((1, 1, 1, 1), dict(c1=1), False),
        ((1, 1, 1), dict(c1=1, c2=1), False),
        ((1, 1, 1, 1, 1), dict(c2=1), False),
        ((1, 1, 1), dict(b2=1, c1=1, c2=1), True),
        ((1, 1), dict(b1=1, b2=1, c1=1, c2=1), True),
        ((1,), dict(a2=1, b1=1, b2=1, c1=1, c2=1), False),
        ((), dict(a1=1, a2=1, b1=1, b2=1, c1=1, c2=1), False),
    ],
)
def test_assert_all_params_set_explicitly(
    args: Tuple[int, ...], kwargs: Dict[str, int], valid: bool
):
    from bioimageio.spec._internal.utils import assert_all_params_set_explicitly

    def func(
        a1: int = 0,
        a2: int = 0,
        /,
        b1: int = 0,
        b2: int = 0,
        *args: Any,
        c1: int = 0,
        c2: int = 0,
        **kwargs: Any,
    ):
        print(a1, a2, b1, b2, args, c1, c2, kwargs)

    func_explicit = assert_all_params_set_explicitly(func)

    func(*args, **kwargs)

    if valid:
        ctxt = nullcontext()
    else:
        ctxt = pytest.raises(AssertionError)

    with ctxt:
        func_explicit(*args, **kwargs)
