from pprint import pformat
from types import TracebackType
from typing import Any, List, Type, Union

from pydantic import ValidationError

from .summary import format_loc

try:
    from IPython.core.getipython import get_ipython
    from IPython.core.interactiveshell import InteractiveShell

    class PrettyValidationError(ValueError):
        """Wrap a pydantic.ValidationError to custumize formatting."""

        def __init__(self, validation_error: ValidationError):
            super().__init__()
            self.error = validation_error

        def __str__(self):
            errors: List[str] = []
            for e in self.error.errors(include_url=False):
                ipt_lines = pformat(
                    e["input"], sort_dicts=False, depth=1, compact=True, width=30
                ).split("\n")
                if len(ipt_lines) > 2:
                    ipt_lines[1:-1] = ["..."]

                ipt = " ".join([il.strip() for il in ipt_lines])

                errors.append(
                    f"\n{format_loc(e['loc'], enclose_in='')}\n  {e['msg']} [input={ipt}]"
                )

            return (
                f"{self.error.error_count()} validation errors for"
                f" {self.error.title}:{''.join(errors)}"
            )

    def _custom_exception_handler(
        self: InteractiveShell,
        etype: Type[ValidationError],
        evalue: ValidationError,
        tb: TracebackType,
        tb_offset: Any = None,
    ):
        assert issubclass(etype, ValidationError), type(etype)
        assert isinstance(evalue, ValidationError), type(etype)

        stb: Union[Any, List[Union[str, Any]]]
        stb = self.InteractiveTB.structured_traceback(  # pyright: ignore[reportUnknownVariableType]
            etype, PrettyValidationError(evalue), tb, tb_offset=tb_offset
        )

        if isinstance(stb, list):
            stb_clean = []
            for line in stb:  # pyright: ignore[reportUnknownVariableType]
                if (
                    isinstance(line, str)
                    and "pydantic" in line
                    and "__tracebackhide__" in line
                ):
                    # ignore pydantic internal frame in traceback
                    continue
                stb_clean.append(line)

            stb = stb_clean

        self._showtraceback(etype, PrettyValidationError(evalue), stb)  # type: ignore

    def enable_pretty_validation_errors_in_ipynb():
        """A modestly hacky way to display prettified validaiton error messages and traceback
        in interactive Python notebooks"""
        ipy = get_ipython()
        if ipy is not None:
            ipy.set_custom_exc((ValidationError,), _custom_exception_handler)

except ImportError:

    def enable_pretty_validation_errors_in_ipynb():
        return
