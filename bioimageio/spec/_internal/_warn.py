import dataclasses
import sys
from logging import getLogger
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Literal,
    Optional,
    Union,
    get_args,
)

from annotated_types import BaseMetadata, GroupedMetadata
from pydantic import FieldValidationInfo, TypeAdapter
from pydantic._internal._decorators import inspect_validator
from pydantic.functional_validators import AfterValidator, BeforeValidator
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import (
    FieldValidatorFunction,
    NoInfoValidatorFunction,
)
from typing_extensions import Annotated, LiteralString

from bioimageio.spec.shared.validation import (
    SEVERITY_TO_WARNING,
    Severity,
    validation_context_var,
)

if TYPE_CHECKING:
    from pydantic.functional_validators import _V2Validator  # type: ignore

# WARNING_LEVEL_CONTEXT_KEY: Literal["warning_level"] = "warning_level"

if sys.version_info < (3, 10):
    SLOTS: Dict[str, Any] = {}
else:
    SLOTS = {"slots": True}


ValidatorFunction = Union[NoInfoValidatorFunction, FieldValidatorFunction]

AnnotationMetaData = Union[BaseMetadata, GroupedMetadata]


def raise_warning(message_template: LiteralString, *, severity: Severity, context: Optional[Dict[str, Any]]):
    raise PydanticCustomError(SEVERITY_TO_WARNING[severity], message_template, context)


def warn(
    typ: Union[AnnotationMetaData, Any],
    severity: Severity = 30,
    msg: Optional[LiteralString] = None,
):
    """treat a type or its annotation metadata as a warning condition"""
    if isinstance(typ, get_args(AnnotationMetaData)):
        typ = Annotated[Any, typ]

    validator = TypeAdapter(typ)
    return BeforeWarner(validator.validate_python, severity=severity, msg=msg)


def call_validator_func(
    func: "_V2Validator",
    mode: Literal["after", "before", "plain", "wrap"],
    value: Any,
    info: FieldValidationInfo,
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
    severity: Severity = 30,
    msg: Optional[LiteralString] = None,
) -> ValidatorFunction:
    """turn validation function into a no-op, based on warning level"""

    def wrapper(value: Any, info: FieldValidationInfo) -> Any:
        logger = getLogger(getattr(info, "field_name", "node"))
        context = validation_context_var.get()
        if severity < context.warning_level:
            return value

        try:
            call_validator_func(func, mode, value, info)
        except (AssertionError, ValueError) as e:
            logger.log(severity, e)
            raise_warning(msg or ",".join(e.args), severity=severity, context=dict(value=value))

        return value

    return wrapper


@dataclasses.dataclass(frozen=True, **SLOTS)
class _WarnerMixin:
    severity: Severity = 30
    msg: Optional[LiteralString] = None

    def __getattribute__(self, __name: str) -> Any:
        ret = super().__getattribute__(__name)
        if __name == "func":
            return as_warning(ret, severity=self.severity, msg=self.msg)
        else:
            return ret


@dataclasses.dataclass(frozen=True, **SLOTS)
class AfterWarner(_WarnerMixin, AfterValidator):
    """Like AfterValidator, but wraps validation `func` with the `warn` decorator"""


@dataclasses.dataclass(frozen=True, **SLOTS)
class BeforeWarner(_WarnerMixin, BeforeValidator):
    """Like BeforeValidator, but wraps validation `func` with the `warn` decorator"""
