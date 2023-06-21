import collections.abc
import contextlib
import dataclasses
from keyword import iskeyword
from multiprocessing import context
import re
from functools import partial
import sys
from typing import (
    Annotated,
    Any,
    Callable,
    Generic,
    Literal,
    Mapping,
    Sequence,
    Type,
    Union,
    get_args,
    TypeVar,
    get_origin,
)
from annotated_types import BaseMetadata, GroupedMetadata, MinLen
import annotated_types

import packaging.version
from pydantic import GetCoreSchemaHandler, TypeAdapter, ValidationInfo
from pydantic._internal._decorators import inspect_validator
from pydantic.functional_validators import AfterValidator, BeforeValidator
from pydantic_core.core_schema import GeneralValidatorFunction, NoInfoValidatorFunction
from pydantic_core import core_schema
from bioimageio.spec.shared.types_ import RawLeafValue, RawMapping

WARNINGS_CONTEXT_KEY: Literal["warnings"] = "warnings"
RAISE_WARNINGS_VALUE: Literal["raise"] = "raise"

if sys.version_info < (3, 10):
    # EllipsisType = type(Ellipsis)
    # KW_ONLY = {}
    SLOTS = {}
else:
    # from types import EllipsisType

    # KW_ONLY = {"kw_only": True}
    SLOTS = {"slots": True}

# somehow it does't work to use runtime checkable Protocols to determine
# if a functional validator takes the info arg or not..
# we use "from pydantic._internal._decorators import inspect_validator" instead
# @runtime_checkable
# class GeneralValidatorFunction(Protocol):
#     def __call__(self, value: Any, /, info: ValidationInfo) -> Any:
#         ...
#
# @runtime_checkable
# class NoInfoValidatorFunction(Protocol):
#     def __call__(self, value: Any, /) -> Any:
#         ...


ValidatorFunction = Union[NoInfoValidatorFunction, GeneralValidatorFunction]

AnnotationMetaData = Union[BaseMetadata, GroupedMetadata]


# class WithWarning(Generic[T, W]):
#     """Allows to add a warning as type W to a type T"""

#     def __init__(self, fail_on: T, warn_on: W) -> None:
#         super().__init__()
#         self.validator = TypeAdapter(fail_on)
#         self.warner = TypeAdapter(warn_on)

#     def __get_pydantic_core_schema__(self, _source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
#         return core_schema.general_plain_validator_function(self._validate)

#     def _validate(self, value: Any, info: ValidationInfo) -> Union[T, W]:
#         valid = self.validator.validate_python(value)
#         if info.context["warnings"] == "raise":
#             valid = self.warner.validate_python(valid)

#         return valid


def warn(typ: Union[AnnotationMetaData, Any]):
    """treat a type or its annotation metadata as a warning condition"""
    assert get_origin(AnnotationMetaData) is Union
    if isinstance(typ, get_args(AnnotationMetaData)):
        typ = Annotated[Any, typ]

    validator = TypeAdapter(typ)
    return BeforeWarner(validator.validate_python)


def as_warning(
    func: ValidatorFunction,
    *,
    mode: Literal["after", "before", "plain", "wrap"] = "after",
) -> GeneralValidatorFunction:
    """turn validation function into a no-op, but may raise if `context["warnings"] == "raise"`"""

    def wrapper(value: Any, info: ValidationInfo) -> Any:
        if info.context[WARNINGS_CONTEXT_KEY] == RAISE_WARNINGS_VALUE:
            assert func is not None
            info_arg = inspect_validator(func, mode)
            if info_arg:
                func(value, info)  # type: ignore
            else:
                func(value)  # type: ignore

        return value

    return wrapper


@dataclasses.dataclass(frozen=True, **SLOTS)
class AfterWarner(AfterValidator):
    """Like AfterValidator, but wraps validation `func` with the `warn` decorator"""

    def __getattribute__(self, __name: str) -> Any:
        ret = super().__getattribute__(__name)
        if __name == "func":
            return as_warning(ret)
        else:
            return ret


@dataclasses.dataclass(frozen=True, **SLOTS)
class BeforeWarner(BeforeValidator):
    """Like BeforeValidator, but wraps validation `func` with the `warn` decorator"""

    def __getattribute__(self, __name: str) -> Any:
        ret = super().__getattribute__(__name)
        if __name == "func":
            return as_warning(ret)
        else:
            return ret


def validate_version(v: str) -> str:
    if not re.fullmatch(r"^\s*" + packaging.version.VERSION_PATTERN + r"\s*$", v, re.VERBOSE | re.IGNORECASE):
        raise ValueError(
            f"'{v}' is not a valid version string, " "see https://packaging.pypa.io/en/stable/version.html for help"
        )
    return v


def validate_identifier(s: str, info: ValidationInfo) -> str:
    if not s.isidentifier():
        raise ValueError(
            f"'{s}' is not a valid (Python) identifier, "
            "see https://docs.python.org/3/reference/lexical_analysis.html#identifiers for details."
        )

    if info.context[WARNINGS_CONTEXT_KEY] == RAISE_WARNINGS_VALUE and iskeyword(s):
        raise ValueError(f"'{s}' is a Python keword.")

    return s


# def validate_relative_path(value: Union[Path, str], info: ValidationInfo):
#     return _validate_relative_path_impl(value, info, RelativePath)


# def validate_relative_file_path(value: Union[Path, str], info: ValidationInfo):
#     return _validate_relative_path_impl(value, info, RelativeFilePath)


# def validate_relative_directory(value: Union[Path, str], info: ValidationInfo):
#     return _validate_relative_path_impl(value, info, RelativeDirectory)


# def _validate_relative_path_impl(value: Union[Path, str], info: ValidationInfo, klass: Type[RelativePath]):
#     if "root" not in info.context:
#         raise PydanticUserError("missing 'root' context for {klass}", code=None)

#     root = info.context["root"]
#     if not isinstance(root, (AnyUrl, Path)):
#         raise ValueError(
#             "{klass} expected root context to be of type 'pathlib.Path' or 'pydantic.AnyUrl', "
#             f"but got {root} of type '{type(root)}'"
#         )

#     return klass(value, root=root)


def is_valid_raw_value(value: Any) -> bool:
    return any(is_valid(value) for is_valid in (is_valid_raw_leaf_value, is_valid_raw_mapping, is_valid_raw_sequence))


def is_valid_raw_leaf_value(value: Any) -> bool:
    return isinstance(value, get_args(RawLeafValue))


def is_valid_raw_mapping(value: Union[Any, Mapping[Any, Any]]) -> bool:
    return isinstance(value, collections.abc.Mapping) and all(
        isinstance(k, str) and is_valid_raw_value(v) for k, v in value.items()
    )


def is_valid_raw_sequence(value: Union[Any, Sequence[Any]]) -> bool:
    return isinstance(value, collections.abc.Sequence) and all(is_valid_raw_value(v) for v in value)


def validate_raw_mapping(value: Mapping[str, Any]) -> RawMapping:
    if not is_valid_raw_mapping(value):
        raise AssertionError(f"{value} is not not valid RawMapping")

    return value
