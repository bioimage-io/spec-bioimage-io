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


def test_get_format_version_tuple_valid():
    from bioimageio.spec._internal.utils import get_format_version_tuple

    assert get_format_version_tuple("0.5.3") == (0, 5, 3)
    assert get_format_version_tuple("1.0.0") == (1, 0, 0)
    assert get_format_version_tuple("10.20.30") == (10, 20, 30)


def test_get_format_version_tuple_invalid():
    from bioimageio.spec._internal.utils import get_format_version_tuple

    assert get_format_version_tuple("0.5") is None
    assert get_format_version_tuple("0.5.3.1") is None
    assert get_format_version_tuple("a.b.c") is None
    assert get_format_version_tuple(123) is None
    assert get_format_version_tuple(None) is None


def test_nest_dict_basic():
    from bioimageio.spec._internal.utils import nest_dict

    result = nest_dict({("a", "b"): 1, ("a", "c"): 2})
    assert result == {"a": {"b": 1, "c": 2}}


def test_nest_dict_single_key():
    from bioimageio.spec._internal.utils import nest_dict

    result = nest_dict({("a",): 1})
    assert result == {"a": 1}


def test_nest_dict_collision():
    from bioimageio.spec._internal.utils import nest_dict

    with pytest.raises(ValueError):
        _ = nest_dict({("a",): 1, ("a", "b"): 2})


def test_nest_dict_with_narrow_first_key():
    from bioimageio.spec._internal.utils import nest_dict_with_narrow_first_key

    result = nest_dict_with_narrow_first_key({("a", "b"): 1}, str)
    assert result == {"a": {"b": 1}}


def test_nest_dict_with_narrow_first_key_invalid():
    from bioimageio.spec._internal.utils import nest_dict_with_narrow_first_key

    with pytest.raises(ValueError):
        _ = nest_dict_with_narrow_first_key({(1, "b"): 1}, str)


def test_unindent_basic():
    from bioimageio.spec._internal.utils import unindent

    text = "    hello\n    world"
    assert unindent(text) == "hello\nworld"


def test_unindent_ignore_first_line():
    from bioimageio.spec._internal.utils import unindent

    text = "summary\n    line1\n    line2"
    result = unindent(text, ignore_first_line=True)
    assert result == "summary\nline1\nline2"


def test_unindent_single_line():
    from bioimageio.spec._internal.utils import unindent

    assert unindent("  hello") == "hello"


def test_get_os_friendly_file_name():
    from bioimageio.spec._internal.utils import get_os_friendly_file_name

    assert get_os_friendly_file_name("hello world") == "hello_world"
    assert get_os_friendly_file_name("my-model!") == "my_model_"
    assert get_os_friendly_file_name("123abc") == "_123abc"


def test_try_all_first_succeeds():
    from bioimageio.spec._internal.utils import try_all

    result = try_all([lambda: 42, lambda: 99])
    assert result == 42


def test_try_all_first_fails_second_succeeds():
    from bioimageio.spec._internal.utils import try_all

    def fail():
        raise ValueError("fail")

    result = try_all([fail, lambda: 99])
    assert result == 99


def test_try_all_all_fail():
    from bioimageio.spec._internal.utils import try_all
    from exceptiongroup import ExceptionGroup

    def fail():
        raise ValueError("fail")

    with pytest.raises(ExceptionGroup):
        try_all([fail, fail])


def test_try_all_raise_last():
    from bioimageio.spec._internal.utils import try_all_raise_last

    def fail():
        raise ValueError("fail")

    with pytest.raises(RuntimeError):
        try_all_raise_last([fail, fail])


def test_try_all_raise_last_success():
    from bioimageio.spec._internal.utils import try_all_raise_last

    result = try_all_raise_last([lambda: 42])
    assert result == 42


def test_pretty_serializer_repr():
    from bioimageio.spec._internal.utils import PrettyPlainSerializer

    s = PrettyPlainSerializer(func=str)
    r = repr(s)
    assert "PrettyPlainSerializer" in r
    assert "str" in r


def test_nest_dict_leaf_then_nested():
    from bioimageio.spec._internal.utils import nest_dict

    # Insert leaf first so the nested key hits the outer ValueError (line 69)
    with pytest.raises(ValueError):
        _ = nest_dict({("a",): 1, ("a", "b"): 2})


def test_pretty_wrap_serializer_repr():
    from bioimageio.spec._internal.utils import PrettyWrapSerializer

    def handler(v: object, nxt: object) -> str:
        return str(v)

    s = PrettyWrapSerializer(func=handler)
    r = repr(s)
    assert "PrettyWrapSerializer" in r
