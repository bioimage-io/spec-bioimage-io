import collections.abc
import re
from functools import partial
from typing import Any, Callable, Literal, Mapping, Sequence, Union, get_args

import packaging.version
from pydantic import ValidationInfo
from pydantic._internal._decorators import inspect_validator
from pydantic._internal._internal_dataclass import slots_dataclass  # std dataclass but with slots=True for py>=3.10
from pydantic.functional_validators import AfterValidator
from pydantic_core.core_schema import GeneralValidatorFunction, NoInfoValidatorFunction

from bioimageio.spec.shared.types_ import RawLeafValue, RawMapping

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


def warn(
    validate_func: Union[ValidatorFunction, None] = None,
    *,
    mode: Literal["after", "before", "plain", "wrap"] = "after",
) -> Union[GeneralValidatorFunction, Callable[[ValidatorFunction], GeneralValidatorFunction]]:
    """turn validation function into a no-op, unless `context["warnings"] == "raise"`"""
    if validate_func is None:
        return partial(warn, mode=mode)  # type: ignore

    def wrapper(value: Any, info: ValidationInfo) -> Any:
        if info.context["warnings"] == "raise":
            assert validate_func is not None
            info_arg = inspect_validator(validate_func, "after")
            if info_arg:
                return validate_func(value, info)  # type: ignore
            else:
                return validate_func(value)  # type: ignore

            # somehow does not work, see commented Protocols above
            # if isinstance(validate_func, GeneralValidatorFunction):
            #     return validate_func(value, info)
            # else:
            #     return validate_func(value)
        else:
            return value

    return wrapper


@slots_dataclass(frozen=True)
class AfterWarner(AfterValidator):
    """wraps validation `func` with the `warn` decorator"""

    def __getattribute__(self, __name: str) -> Any:
        ret = super().__getattribute__(__name)
        if __name == "func":
            return warn(ret)
        else:
            return ret


def validate_version(v: str) -> str:
    if not re.fullmatch(r"^\s*" + packaging.version.VERSION_PATTERN + r"\s*$", v, re.VERBOSE | re.IGNORECASE):
        raise ValueError(
            f"'{v}' is not a valid version string, " "see https://packaging.pypa.io/en/stable/version.html for help"
        )
    return v


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
