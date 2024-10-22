import dataclasses
import sys
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Union, get_args

import pydantic.functional_validators
from annotated_types import BaseMetadata, GroupedMetadata
from loguru import logger
from pydantic import TypeAdapter
from pydantic._internal._decorators import inspect_validator
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import (
    NoInfoValidatorFunction,
    ValidationInfo,
    WithInfoValidatorFunction,
)
from typing_extensions import Annotated, LiteralString

from .validation_context import validation_context_var
from .warning_levels import WARNING, WarningSeverity

if TYPE_CHECKING:
    from pydantic.functional_validators import _V2Validator  # type: ignore

if sys.version_info < (3, 10):
    SLOTS: Dict[str, Any] = {}
else:
    SLOTS = {"slots": True}


ValidatorFunction = Union[NoInfoValidatorFunction, WithInfoValidatorFunction]

AnnotationMetaData = Union[BaseMetadata, GroupedMetadata]


def warn(
    typ: Union[AnnotationMetaData, Any],
    msg: LiteralString,  # warning message, e.g. "'{value}' incompatible with {typ}
    severity: WarningSeverity = WARNING,
):
    """treat a type or its annotation metadata as a warning condition"""
    if isinstance(typ, get_args(AnnotationMetaData)):
        typ = Annotated[Any, typ]

    validator: TypeAdapter[Any] = TypeAdapter(typ)

    return AfterWarner(
        validator.validate_python, severity=severity, msg=msg, context={"typ": typ}
    )


def call_validator_func(
    func: "_V2Validator",
    mode: Literal["after", "before", "plain", "wrap"],
    value: Any,
    info: ValidationInfo,
) -> Any:
    info_arg = inspect_validator(func, mode)
    if info_arg:
        return func(value, info)  # type: ignore
    else:
        return func(value)  # type: ignore


def as_warning(
    func: "_V2Validator",
    *,
    mode: Literal["after", "before", "plain", "wrap"] = "after",
    severity: WarningSeverity = WARNING,
    msg: Optional[LiteralString] = None,
    msg_context: Optional[Dict[str, Any]] = None,
) -> ValidatorFunction:
    """turn validation function into a no-op, based on warning level"""

    def wrapper(value: Any, info: ValidationInfo) -> Any:
        try:
            call_validator_func(func, mode, value, info)
        except (AssertionError, ValueError) as e:
            issue_warning(
                msg or ",".join(e.args),
                value=value,
                severity=severity,
                msg_context=msg_context,
            )

        return value

    return wrapper


@dataclasses.dataclass(frozen=True, **SLOTS)
class AfterWarner(pydantic.functional_validators.AfterValidator):
    """Like AfterValidator, but wraps validation `func` `as_warning`"""

    severity: WarningSeverity = WARNING
    msg: Optional[LiteralString] = None
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "func",
            as_warning(
                self.func,
                mode="after",
                severity=self.severity,
                msg=self.msg,
                msg_context=self.context,
            ),
        )


@dataclasses.dataclass(frozen=True, **SLOTS)
class BeforeWarner(pydantic.functional_validators.BeforeValidator):
    """Like BeforeValidator, but wraps validation `func` `as_warning`"""

    severity: WarningSeverity = WARNING
    msg: Optional[LiteralString] = None
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "func",
            as_warning(
                self.func,
                mode="before",
                severity=self.severity,
                msg=self.msg,
                msg_context=self.context,
            ),
        )


# TODO: add `loc: Loc` to `issue_warning()`
#   and use a loguru handler to format warnings accordingly
def issue_warning(
    msg: LiteralString,
    *,
    value: Any,
    severity: WarningSeverity = WARNING,
    msg_context: Optional[Dict[str, Any]] = None,
    field: Optional[str] = None,
):
    msg_context = {"value": value, "severity": severity, **(msg_context or {})}
    if severity >= validation_context_var.get().warning_level:
        raise PydanticCustomError("warning", msg, msg_context)
    elif validation_context_var.get().log_warnings:
        log_msg = (field + ": " if field else "") + (msg.format(**msg_context))
        logger.opt(depth=1).log(severity, log_msg)
