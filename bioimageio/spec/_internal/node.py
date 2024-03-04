from __future__ import annotations

from typing import (
    Any,
    Dict,
    Optional,
    Union,
)

import pydantic
from typing_extensions import (
    Self,
)

from .validation_context import ValidationContext, validation_context_var


class Node(
    pydantic.BaseModel,
    extra="forbid",
    frozen=False,
    populate_by_name=True,
    revalidate_instances="never",
    validate_assignment=True,
    validate_default=False,
    validate_return=True,  # TODO: check if False here would bring a speedup and can still be safe
    # use_attribute_docstrings=True,  TODO: use this from future pydantic 2.7
    # see https://github.com/pydantic/pydantic/issues/5656
):
    """Subpart of a resource description"""

    @classmethod
    def model_validate(
        cls,
        obj: Union[Any, Dict[str, Any]],
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Union[ValidationContext, Dict[str, Any], None] = None,
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
            context = validation_context_var.get()
        elif isinstance(context, dict):
            context = ValidationContext(**context)

        if isinstance(obj, dict):
            assert all(isinstance(k, str) for k in obj), obj

        with context:
            # use validation context as context manager for equal behavior of __init__ and model_validate
            return super().model_validate(
                obj, strict=strict, from_attributes=from_attributes
            )
