from __future__ import annotations

import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_file_location
from types import ModuleType
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

import bioimageio.spec._pretty_validation_errors as pretty_validation_errors


def load_module() -> ModuleType:
    # Execute import-time setup without changing the module used by the package.
    spec = spec_from_file_location(
        "bioimageio.spec._pretty_validation_errors_test",
        pretty_validation_errors.__file__,
    )
    assert spec is not None and isinstance(spec.loader, SourceFileLoader)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def pretty_errors(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.setattr("IPython.core.getipython.get_ipython", lambda: None)
    return load_module()


@pytest.fixture
def validation_error() -> ValidationError:
    return ValidationError.from_exception_data(
        "Example",
        [
            {"type": "int_parsing", "loc": ("items", 0), "input": "bad"},
            {"type": "missing", "loc": ("name",), "input": {}},
        ],
    )


def test_format_multiple_errors(
    pretty_errors: ModuleType, validation_error: ValidationError
):
    error = pretty_errors.PrettyValidationError(validation_error)
    assert error.error is validation_error
    assert isinstance(error, ValueError)
    assert str(error) == (
        "2 validation errors for Example:\nitems.0\n"
        "  Input should be a valid integer, unable to parse string as an integer"
        " [input='bad']\nname\n  Field required [input={}]"
    )


@pytest.mark.parametrize(
    "value, formatted",
    [
        ({"z": {"nested": 1}, "a": [1, 2]}, "{'z': {...}, 'a': [...]}"),
        (list(range(20)), "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ... 17, 18, 19]"),
        (list(range(9)), "[0, 1, 2, 3, 4, 5, 6, 7, 8]"),
    ],
)
def test_format_input(pretty_errors: ModuleType, value: object, formatted: str):
    error = ValidationError.from_exception_data(
        "Example", [{"type": "int_type", "loc": (), "input": value}]
    )
    assert str(pretty_errors.PrettyValidationError(error)) == (
        "1 validation errors for Example:\n\n"
        f"  Input should be a valid integer [input={formatted}]"
    )


@pytest.mark.parametrize("as_list", [True, False])
def test_custom_exception_handler(
    pretty_errors: ModuleType, validation_error: ValidationError, as_list: bool
):
    lines = [
        "user frame",
        "pydantic frame with __tracebackhide__",
        "pydantic frame without marker",
        "user frame with __tracebackhide__",
        42,
    ]
    traceback = lines if as_list else tuple(lines)
    shell = Mock()
    shell.InteractiveTB.structured_traceback.return_value = traceback
    pretty_errors._custom_exception_handler(
        shell, ValidationError, validation_error, None, tb_offset=2
    )
    args, kwargs = shell.InteractiveTB.structured_traceback.call_args
    assert args[0] is ValidationError
    assert args[1].error is validation_error
    assert args[2] is None
    assert kwargs == {"tb_offset": 2}
    shown_type, shown_error, shown_traceback = shell._showtraceback.call_args.args
    assert shown_type is ValidationError
    assert shown_error.error is validation_error
    assert shown_traceback == (lines[:1] + lines[2:] if as_list else traceback)


@pytest.mark.parametrize(
    "error_type, error_value",
    [(ValueError, ValueError()), (ValidationError, ValueError())],
)
def test_custom_exception_handler_rejects_other_errors(
    pretty_errors: ModuleType, error_type: type[Exception], error_value: Exception
):
    shell = Mock()
    with pytest.raises(AssertionError):
        pretty_errors._custom_exception_handler(shell, error_type, error_value, None)
    shell.InteractiveTB.structured_traceback.assert_not_called()
    shell._showtraceback.assert_not_called()


def test_import_without_ipython(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setitem(sys.modules, "IPython.core.getipython", None)
    assert load_module().PRETTY_VALIDATION_ERRORS_IN_IPYNB_ENABLED is False


def test_import_without_shell(pretty_errors: ModuleType):
    assert pretty_errors.PRETTY_VALIDATION_ERRORS_IN_IPYNB_ENABLED is True


def test_import_registers_handler(monkeypatch: pytest.MonkeyPatch):
    shell = Mock()
    monkeypatch.setattr("IPython.core.getipython.get_ipython", lambda: shell)
    module = load_module()
    shell.set_custom_exc.assert_called_once_with(
        (ValidationError,), module._custom_exception_handler
    )
    assert module.PRETTY_VALIDATION_ERRORS_IN_IPYNB_ENABLED is True


def test_import_warns_on_registration_failure(monkeypatch: pytest.MonkeyPatch):
    shell = Mock()
    shell.set_custom_exc.side_effect = RuntimeError("registration failed")
    monkeypatch.setattr("IPython.core.getipython.get_ipython", lambda: shell)
    with pytest.warns(
        UserWarning,
        match="Failed to enable pretty validation errors in ipython: registration failed",
    ):
        module = load_module()
    assert module.PRETTY_VALIDATION_ERRORS_IN_IPYNB_ENABLED is False
