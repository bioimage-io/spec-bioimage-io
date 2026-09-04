from __future__ import annotations

import collections.abc
import warnings
from typing import (
    Any,
    Callable,
    Literal,
    Mapping,
)

import pydantic
from typing_extensions import ParamSpec, Self, TypeVar

from .type_guards import is_kwargs, is_mapping
from .validation_context import ValidationContext, get_validation_context


def _node_title_generator(node: type[Node]) -> str:
    return (
        f"{node.implemented_type} {node.implemented_format_version}"  # pyright: ignore[reportAttributeAccessIssue]
        if hasattr(node, "implemented_type")
        and hasattr(node, "implemented_format_version")
        else f"{node.__module__.replace('bioimageio.spec.', '')}.{node.__name__}"
    )


P = ParamSpec("P")
T = TypeVar("T")


class Node(
    pydantic.BaseModel,
    allow_inf_nan=False,
    extra="forbid",
    frozen=False,
    model_title_generator=_node_title_generator,
    populate_by_name=True,
    revalidate_instances="always",
    use_attribute_docstrings=True,
    validate_assignment=True,
    validate_default=True,
    validate_return=True,
):
    # empty docstring to remove all pydantic docstrings from the pdoc spec docs
    """"""  # ruff: ignore[D419]

    @classmethod
    def model_validate(
        cls,
        obj: Any | Mapping[str, Any],
        *,
        strict: bool | None = None,
        extra: Literal["allow", "ignore", "forbid"] | None = None,
        from_attributes: bool | None = None,
        context: ValidationContext | Mapping[str, Any] | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        """Validate a pydantic model instance.

        Args:
            obj: The object to validate.
            strict: Whether to raise an exception on invalid fields.
            from_attributes: Whether to extract data from object attributes.
            context: Additional context to pass to the validator.

        Raises:
            ValidationError: If the object failed validation.

        Returns:
            The validated description instance.
        """
        __tracebackhide__ = True

        if context is None:
            context = get_validation_context()
        elif isinstance(context, collections.abc.Mapping):
            context = ValidationContext(**context)

        assert not is_mapping(obj) or is_kwargs(obj), obj

        # TODO: pass on extra with pydantic >=2.12
        if extra is not None:
            warnings.warn("`extra` argument is currently ignored")

        with context:
            # use validation context as context manager for equal behavior of __init__ and model_validate
            return super().model_validate(
                obj, strict=strict, from_attributes=from_attributes
            )

    @classmethod
    def dict_from_kwargs(
        cls: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> dict[str, Any]:
        assert not args, "Did not expected any args"
        return dict(kwargs)
