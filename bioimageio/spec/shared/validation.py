import collections.abc
import dataclasses
import re
import sys
from datetime import datetime
from keyword import iskeyword
from logging import getLogger
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Literal,
    Mapping,
    Sequence,
    Union,
    get_args,
    get_origin,
)

import packaging.version
from annotated_types import BaseMetadata, GroupedMetadata, Interval
from pydantic import AnyUrl, TypeAdapter, ValidationInfo
from pydantic._internal._decorators import inspect_validator
from pydantic.functional_validators import AfterValidator, BeforeValidator
from pydantic_core.core_schema import GeneralValidatorFunction, NoInfoValidatorFunction
from typing_extensions import Annotated

if TYPE_CHECKING:
    from bioimageio.spec.shared.types import FileSource


WARNINGS_ACTION_KEY = "warnings_action"
RAISE_WARNINGS = "raise"

ALERT = 35  # no ALERT or worse -> RDF is worriless
WARNING = 30  # no WARNING or worse -> RDF is watertight
INFO = 20

if sys.version_info < (3, 10):
    SLOTS: Dict[str, Any] = {}
else:
    SLOTS = {"slots": True}


ValidatorFunction = Union[NoInfoValidatorFunction, GeneralValidatorFunction]

AnnotationMetaData = Union[BaseMetadata, GroupedMetadata]


def warn(typ: Union[AnnotationMetaData, Any], severity: Annotated[int, Interval(ge=0, le=50)] = INFO):
    """treat a type or its annotation metadata as a warning condition"""
    assert get_origin(AnnotationMetaData) is Union
    if isinstance(typ, get_args(AnnotationMetaData)):
        typ = Annotated[Any, typ]

    validator = TypeAdapter(typ)
    return BeforeWarner(validator.validate_python, severity=severity)


def as_warning(
    func: GeneralValidatorFunction,
    *,
    mode: Literal["after", "before", "plain", "wrap"] = "after",
    severity: Annotated[int, Interval(ge=0, le=50)] = INFO,
) -> GeneralValidatorFunction:
    """turn validation function into a no-op, but may raise if `context["warnings"] == "raise"`"""

    def wrapper(value: Any, info: ValidationInfo) -> Any:
        logger = getLogger("node")
        if logger.level <= severity:
            try:
                info_arg = inspect_validator(func, mode)
                if info_arg:
                    func(value, info)  # type: ignore
                else:
                    func(value)  # type: ignore
            except Exception as e:
                logger.log(severity, e)
                if info.context is not None and info.context.get(WARNINGS_ACTION_KEY) == RAISE_WARNINGS:
                    raise e  # from None ?

        return value

    return wrapper


# def as_warning_with_kwargs(
#     mode: Literal["after", "before", "plain", "wrap"] = "after",
#     severity: Annotated[int, Interval(ge=0, le=50)] = INFO,
# ):
#     def decorated(cls, func: GeneralValidatorFunction):
#         return as_warning(cls, func, mode=mode, severity=severity)

#     return decorated


@dataclasses.dataclass(frozen=True, **SLOTS)
class _WarnerMixin:
    severity: Annotated[int, Interval(ge=0, le=50)] = INFO

    def __getattribute__(self, __name: str) -> Any:
        ret = super().__getattribute__(__name)
        if __name == "func":
            return as_warning(ret, severity=self.severity)
        else:
            return ret


@dataclasses.dataclass(frozen=True, **SLOTS)
class AfterWarner(_WarnerMixin, AfterValidator):
    """Like AfterValidator, but wraps validation `func` with the `warn` decorator"""


@dataclasses.dataclass(frozen=True, **SLOTS)
class BeforeWarner(_WarnerMixin, BeforeValidator):
    """Like BeforeValidator, but wraps validation `func` with the `warn` decorator"""


def validate_version(v: str) -> str:
    if not re.fullmatch(r"^\s*" + packaging.version.VERSION_PATTERN + r"\s*$", v, re.VERBOSE | re.IGNORECASE):
        raise ValueError(
            f"'{v}' is not a valid version string, " "see https://packaging.pypa.io/en/stable/version.html for help"
        )
    return v


def validate_identifier(s: str) -> str:
    if not s.isidentifier():
        raise ValueError(
            f"'{s}' is not a valid (Python) identifier, "
            "see https://docs.python.org/3/reference/lexical_analysis.html#identifiers for details."
        )

    return s


def validate_is_not_keyword(s: str) -> str:
    if iskeyword(s):
        raise ValueError(f"'{s}' is a Python keyword and not allowed here.")

    return s


def is_valid_raw_value(value: Any) -> bool:
    return any(is_valid(value) for is_valid in (is_valid_raw_leaf_value, is_valid_raw_mapping, is_valid_raw_sequence))


def is_valid_raw_leaf_value(value: Any) -> bool:
    from bioimageio.spec.shared.types import RawLeafValue

    return isinstance(value, get_args(RawLeafValue))


def is_valid_raw_mapping(value: Union[Any, Mapping[Any, Any]]) -> bool:
    return isinstance(value, collections.abc.Mapping) and all(
        isinstance(k, str) and is_valid_raw_value(v) for k, v in value.items()
    )


def is_valid_raw_sequence(value: Union[Any, Sequence[Any]]) -> bool:
    return isinstance(value, collections.abc.Sequence) and all(is_valid_raw_value(v) for v in value)


def validate_datetime_iso8601(value: Union[datetime, str, Any]) -> datetime:
    if isinstance(value, datetime):
        return value
    elif isinstance(value, str):
        return datetime.fromisoformat(value)
    else:
        raise ValueError(f"Got invalid datetime {value}")


def validate_suffix(value: "FileSource", *suffixes: str) -> "FileSource":
    assert all(suff.startswith(".") for suff in suffixes)
    if isinstance(value, AnyUrl):
        if value.path is None or "." not in value.path:
            suffix = None
        else:
            suffix = "." + value.path.split(".")[-1]
    else:
        suffix = value.relative.suffixes[-1]

    if suffix not in suffixes:
        raise ValueError(f"{suffix} not in {suffixes}")

    return value
