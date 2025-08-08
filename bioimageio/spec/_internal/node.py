from __future__ import annotations

import collections.abc
from typing import (
    Any,
    Mapping,
    Optional,
    Type,
    Union,
)

import pydantic
from typing_extensions import Self

from .type_guards import is_kwargs
from .validation_context import ValidationContext, get_validation_context


def _node_title_generator(node: Type[Node]) -> str:
    return (
        f"{node.implemented_type} {node.implemented_format_version}"  # pyright: ignore[reportAttributeAccessIssue]
        if hasattr(node, "implemented_type")
        and hasattr(node, "implemented_format_version")
        else f"{node.__module__.replace('bioimageio.spec.', '')}.{node.__name__}"
    )


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
    """"""  # empty docstring to remove all pydantic docstrings from the pdoc spec docs

    @classmethod
    def model_validate(
        cls,
        obj: Union[Any, Mapping[str, Any]],
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Union[ValidationContext, Mapping[str, Any], None] = None,
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

        assert not isinstance(obj, collections.abc.Mapping) or is_kwargs(obj), obj

        with context:
            # use validation context as context manager for equal behavior of __init__ and model_validate
            return super().model_validate(
                obj, strict=strict, from_attributes=from_attributes
            )
